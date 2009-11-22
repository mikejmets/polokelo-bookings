import os
from datetime import datetime
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
from models.bookinginfo import Enquiry, AccommodationElement
from controllers.bookingstool import BookingsTool
from models.codelookup import getItemDescription

from controllers import generator

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
        enquiry = Enquiry(
            key_name=enquiry_number, 
            referenceNumber=enquiry_number)
        enquiry.creator = users.get_current_user()
        enquiry.created = datetime.now()
        enquiry.referenceNumber = enquiry_number
        enquiry.guestEmail = node.findtext('email')
        enquiry.agentCode = node.findtext('guestagentcode')
        enquiry.state = 'Temporary'
        enquiry.xmlSource = tostring(node)
        enquiry.put()


        accommodation = AccommodationElement(
            parent=enquiry,
            start=datetime.strptime(node.findtext('startdate'), 
                                        '%Y-%m-%d').date())
        accommodation.creator = users.get_current_user()
        accommodation.created = datetime.now()
        accommodation.city = getItemDescription('CTY',
                                    node.findtext('city'))
        accommodation.type = getItemDescription('ACTYP', 
                                    node.findtext('accommodationtype'))
        accommodation.nights = int(node.findtext('duration'))
        accommodation.genderSensitive = node.findtext('guestgendersensitive') == 'yes'
        adults = node.find('adults')
        accommodation.adultMales = int(adults.findtext('male'))
        accommodation.adultFemales = int(adults.findtext('female'))
        children = node.find('children')
        accommodation.childMales = int(children.findtext('male'))
        accommodation.childFemales = int(children.findtext('female'))
        disability = node.find('disability')
        accommodation.wheelchair = disability.findtext('wheelchairaccess') == 'yes'
        accommodation.specialNeeds = disability.findtext('otherspecialneeds') == 'yes'
        accommodation.xmlSource = tostring(node)
        accommodation.put()


        # get the bookings tool
        bt = BookingsTool()

        # do the availability check
        available, amount, expiry = bt.checkAvailability(enquiry)
        available = available and 'available' or 'not available'

        # append the result as a sub element to the node element
        search_elem = SubElement(node, 'searchresult')
        avail_elem = SubElement(search_elem, 'availability')
        avail_elem.text = available
        amount_elem = SubElement(search_elem, 'zaramount')
        amount_elem.text = str(amount)
        expiry_elem = SubElement(search_elem, 'expirydate')
        expiry_elem.text = str(expiry)

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
