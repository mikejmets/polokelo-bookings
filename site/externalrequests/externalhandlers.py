import os
from datetime import datetime, timedelta
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import datastore_errors
from google.appengine.api import users

from xml.etree.ElementTree import XML, SubElement, tostring

# from models.bookinginfo import ContractedBooking
from models.clientinfo import Client
from models.bookinginfo import EnquiryCollection, Enquiry, \
                                AccommodationElement, GuestElement
from models.codelookup import getItemDescription
from models.packages import Package

from controllers.bookingstool import BookingsTool
from controllers import generator
from workflow.__init__ import ENQUIRY_WORKFLOW

class ExternalBookings(webapp.RequestHandler):
    """ Handler class for all enquiry/booking requests from
        the pulic sites.
    """

    def _checkAvailability(self, node):
        """ Handle the initial check for available slots on an enquiry
        """
        # retrieve all the data from the xml
        enquiry_number = node.findtext('enquirynumber') 

        # check if the browser is submitting the same enquiry again
        # and raise an error.
        enquiry = Enquiry.get_by_key_name(enquiry_number)
        if enquiry:
            # append the result as a sub element to the node element
            search_elem = SubElement(node, 'searchresult')
            # append the error element
            error_element = SubElement(node, 'systemerror')
            error_code = SubElement(error_element, 'errorcode')
            error_code.text = '101'
            error_msg = SubElement(error_element, 'errormessage')
            error_msg.text = 'The enquiry with number %s has already been submitted' % \
                                                    enquiry_number
            # return the result as xml
            return tostring(node)

        # instantiate enquiry and accommodation classes
        enquiry = Enquiry(key_name=enquiry_number, 
                          referenceNumber=enquiry_number)
        enquiry.creator = users.get_current_user()
        enquiry.guestEmail = node.findtext('email')
        enquiry.agentCode = node.findtext('guestagentcode')
        enquiry.xmlSource = tostring(node)
        enquiry.put()
        enquiry.enterWorkflow(ENQUIRY_WORKFLOW)


        accommodation = AccommodationElement(
                            parent=enquiry,
                            start=datetime.strptime(node.findtext('startdate'), 
                                        '%Y-%m-%d').date())
        accommodation.creator = users.get_current_user()
        accommodation.city = getItemDescription('CTY',
                                    node.findtext('city'))
        accomnode = node.find('accommodation')
        accommodation.type = getItemDescription('ACTYP', 
                                    accomnode.findtext('type'))
        if accommodation.type in ['HOM', 'GH']:
            roomsnode = accomnode.find('rooms')
            accommodation.singlerooms = roomsnode.findtext('single')
            accommodation.doublerooms = roomsnode.findtext('double')
            accommodation.twinrooms = roomsnode.findtext('twin')
            accommodation.familyrooms = roomsnode.findtext('family')
        accommodation.nights = int(node.findtext('duration'))
        accommodation.adults = int(node.findtext('adults'))
        accommodation.children = int(node.findtext('children'))
        disability = node.find('disability')
        accommodation.wheelchairAccess = disability.findtext('wheelchairaccess') == 'yes'
        accommodation.specialNeeds = disability.findtext('otherspecialneeds') == 'yes'
        accommodation.xmlSource = tostring(node)
        accommodation.put()


        # get the bookings tool
        bt = BookingsTool()

        # do the availability check
        available, amount = bt.checkAvailability(enquiry)
        if not available:
            enquiry.doTransition('assigntouser')
        enquiry.quoteInZAR = amount
        enquiry.put()

        # append the result as a sub element to the node element
        search_elem = SubElement(node, 'searchresult')
        avail_elem = SubElement(search_elem, 'availability')
        avail_elem.text = available and 'available' or 'not available'
        amount_elem = SubElement(search_elem, 'amount')
        amount_elem.text = str(amount)
        expiry_elem = SubElement(search_elem, 'expirydate')
        expiry_elem.text = str(enquiry.expiryDate)

        # append the error element
        error_element = SubElement(node, 'systemerror')
        error_code = SubElement(error_element, 'errorcode')
        error_code.text = '0'
        error_msg = SubElement(error_element, 'errormessage')

        # return the result as xml
        return tostring(node)


    def _confirmEnquiries(self, node):
        """ confirm the final list of enquiries
        """
        # retrieve the enquiry number
        enquiry_number = node.findtext('enquirynumber') 

        # check if the browser is submitting the same confirmation again
        # and raise an error.
        enquiry_collection = EnquiryCollection.get_by_key_name(enquiry_number)
        if enquiry_collection:
            # append the result as a sub element to the node element
            confirm_elem = SubElement(node, 'confirmationresult')
            # append the error element
            error_element = SubElement(node, 'systemerror')
            error_code = SubElement(error_element, 'errorcode')
            error_code.text = '102'
            error_msg = SubElement(error_element, 'errormessage')
            error_msg.text = 'The enquiry with number %s has already been confirmed' % \
                                                    enquiry_number
            # return the result as xml
            return tostring(node)

        # instantiate the enquiry collection
        enquiry_collection = EnquiryCollection(key_name=enquiry_number,
                                               referenceNumber = enquiry_number)
        enquiry_collection.creator = users.get_current_user()
        enquiry_collection.put()

        # create the primary guest (credit card holder)
        guest_node = node.find('creditcardholder')
        if guest_node:
            # am I setting the parent correctly here?
            guest_element = GuestElement(parent=enquiry_collection,
                                         surname = guest_node.findtext('surname'),
                                         firstNames = guest_node.findtext('name'))
            guest_element.isPrimary = True
            guest_element.email = guest_node.findtext('email')
            guest_element.contactNumber = guest_node.findtext('telephone')
            guest_element.identifyingNumber = guest_node.findtext('passportnumber')
            guest_element.xmlSource = tostring(guest_node)
            guest_element.put()
            # logging.info(tostring(guest_node))

        # update the individual enquiries to have the collection
        # as their parent, and extend their expiry dates for 24 hours
        # in anticipation of the deposit
        enquiry_elements = node.find('enquiries').findall('enquiry')
        for enquiry_element in enquiry_elements:
            # logging.info(tostring(enquiry_element))
            refnum = enquiry_element.findtext('number')
            # retrieve the existing enquiry
            enquiry = Enquiry.get_by_key_name(refnum)
            if enquiry:
                # hope this works properly!!!
                enquiry.parent = enquiry_collection
                enquiry.enqColl = enquiry_collection
                enquiry.xmlSource = tostring(enquiry_element)
                enquiry.put()
                # add the enquiries to the guest element, if it exists
                if guest_node:
                    if enquiry.key() not in guest_element.enquiries:
                        guest_element.enquiries.append(enquiry.key())
                        guest_element.put()

        # append the result
        confirm_elem = SubElement(node, 'confirmationresult')
        result_elem = SubElement(confirm_elem, 'result')
        result_elem.text = enquiry_number
        expiry_elem = SubElement(confirm_elem, 'expirydate')
        expiry_date = datetime.now() + timedelta(hours=24)
        expiry_elem.text = str(expiry_date)

        # append the error element
        error_element = SubElement(node, 'systemerror')
        error_code = SubElement(error_element, 'errorcode')
        error_code.text = '0'
        error_msg = SubElement(error_element, 'errormessage')

        # return the result as xml
        return tostring(node)



    def post(self):
        """ Primary interface for enquiries, bookings and payments
            coming from the public sites
        """
        # get the xml enquiry sent to us
        xml = self.request.body
        logging.info(xml)

        # create the xml element tree
        xmlroot = XML(xml)
        
        # find out what we need to do
        action = xmlroot.findtext('action')

        # execute the approptiate action
        if action.lower() == 'check availability':
            # initial enquiry to check for availability
            result = self._checkAvailability(xmlroot)

        elif action.lower() == 'confirm enquiries':
            # initial enquiry to check for availability
            result = self._confirmEnquiries(xmlroot)

        elif action.lower() == 'generate enquiry number':
            number_element = SubElement(xmlroot, 'enquirynumber')
            number_element.text = generator.generateEnquiryNumber()
            result = tostring(xmlroot)

        else:
            # send back an error informing the public site
            # that we have no clue what it wants
            error_elem = SubElement(xmlroot, 'error')
            error_elem.text = 'Unable to determine what to do'
            result = tostring(xmlroot)
 
        # return the result
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(result)


application = webapp.WSGIApplication([
                  ('/externalbookings', ExternalBookings),
                  ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
