import os
import sys
from datetime import datetime
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
# from google.appengine.ext.db import run_in_transaction

from xml.etree.ElementTree import XML, SubElement, tostring

from models.bookinginfo import EnquiryCollection, Enquiry, CollectionTransaction, \
                                AccommodationElement, GuestElement
from models.enquiryroot import EnquiryRoot
from models.hostinfo import EmailAddress, PhoneNumber
from models.clientinfo import Client
from models.codelookup import getItemDescription

from controllers.bookingstool import BookingsTool
from controllers import generator
from externalrequests import retrieveinvoice

class ExternalBookings(webapp.RequestHandler):
    """ Handler class for all enquiry/booking requests from
        the pulic sites.
    """

    def _addErrorNode(self, node, code='0', message=None):
        error_element = SubElement(node, 'systemerror')
        error_code = SubElement(error_element, 'errorcode')
        error_code.text = code
        error_msg = SubElement(error_element, 'errormessage')
        if message is not None:
            error_msg.text = message

    def _checkAvailability(self, node):
        """ Handle the initial check for available slots on an enquiry
        """
        # retrieve the enquiry batch number and 
        # create or get the enquiry collection instance
        batch_number = node.findtext('enquirybatchnumber')
        enquiry_collection = EnquiryCollection.get_or_insert( \
                                        key_name=batch_number,
                                        parent=EnquiryRoot.getEnquiryRoot(),
                                        referenceNumber=batch_number)
        enquiry_collection.creator = users.get_current_user()
        enquiry_collection.put()

        # retrieve all the enquiry number
        enquiry_number = node.findtext('enquirynumber')

        # check if the browser is submitting the same enquiry again
        # and raise an error.
        enquiry = Enquiry.get_by_key_name(enquiry_number, parent=enquiry_collection)
        if enquiry:
            # append the result as a sub element to the node element
            search_elem = SubElement(node, 'searchresult')
            # append the error element
            self._addErrorNode(node, '101', 
                    'The enquiry with number %s has already been submitted' % \
                                                    enquiry_number)
            # return the result as xml
            return tostring(node)

        # instantiate enquiry and accommodation classes
        enquiry = Enquiry(parent=enquiry_collection,
                          key_name=enquiry_number, 
                          referenceNumber=enquiry_number)
        enquiry.creator = users.get_current_user()
        enquiry.guestEmail = node.findtext('email')
        enquiry.agentCode = node.findtext('guestagentcode')
        enquiry.xmlSource = tostring(node)
        enquiry.put()
        enquiry.enterWorkflow(EnquiryRoot.getEnquiryWorkflow())

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
            enquiry.doTransition('putonhold')
        enquiry.quoteInZAR = amount
        enquiry.vatInZAR = long(amount * 0.14)
        enquiry.totalAmountInZAR = enquiry.quoteInZAR + enquiry.vatInZAR
        enquiry.put()

        # append the result as a sub element to the node element
        search_elem = SubElement(node, 'searchresult')
        avail_elem = SubElement(search_elem, 'availability')
        avail_elem.text = available and 'available' or 'not available'
        amount_elem = SubElement(search_elem, 'amount')
        amount_elem.text = "%0.2f" % (enquiry.quoteInZAR / 100.0)
        amount_elem = SubElement(search_elem, 'vat')
        amount_elem.text = "%0.2f" % (enquiry.vatInZAR / 100.0)

        # append the error element
        self._addErrorNode(node)

        # return the result as xml
        return tostring(node)


    def _confirmEnquiries(self, node):
        """ confirm the final list of enquiries
        """
        # retrieve the enquiry batch number and collection instance
        collection_number = node.findtext('enquirybatchnumber') 
        enquiry_collection = EnquiryCollection.get_by_key_name( \
                                        collection_number, 
                                        parent=EnquiryRoot.getEnquiryRoot())

        # locate the primary guest node (credit card holder)
        guest_node = node.find('creditcardholder')

        # update the individual enquiries to have the collection
        # as their parent, and extend their expiry dates for 24 hours
        # in anticipation of the deposit
        enquiry_elements = node.find('enquiries').findall('enquiry')

        for enquiry_element in enquiry_elements:
            # initialise the booking transaction data
            txn_description = 'Booking confirmation on %s: REFERENCE %s\n' % \
                                (datetime.now().date(), collection_number)
            txn_total = 0L
            txn_vat = 0L
            txn_quote = 0L

            # logging.info(tostring(enquiry_element))
            refnum = enquiry_element.findtext('enquirynumber')
            # retrieve the existing enquiry
            enquiry = Enquiry.get_by_key_name(refnum, parent=enquiry_collection)
            if enquiry:
                # do the transitions
                if enquiry.getStateName() == 'allocated':
                    txn_description += '%s: %s\n' % \
                                (refnum, enquiry.getAccommodationDescription())
                    txn_total = enquiry.totalAmountInZAR 
                    txn_vat = enquiry.vatInZAR
                    txn_quote = enquiry.quoteInZAR
                    enquiry.doTransition('confirmfromallocated', 
                                        txn_description=txn_description,
                                        txn_total=txn_total,
                                        txn_vat=txn_vat,
                                        txn_quote=txn_quote,
                                        txn_category='Auto',
                                        txn_notes='')
                elif enquiry.getStateName() == 'onhold':
                    enquiry.doTransition('assigntoagent')

                if guest_node:
                    guest_element = GuestElement( \
                                        key_name=guest_node.findtext('passportnumber'),
                                        parent=enquiry_collection,
                                        surname=guest_node.findtext('surname'),
                                        firstNames=guest_node.findtext('name'))
                    guest_element.creator = users.get_current_user()
                    guest_element.isPrimary = True
                    guest_element.email = guest_node.findtext('email')
                    guest_element.contactNumber = guest_node.findtext('telephone')
                    guest_element.identifyingNumber = guest_node.findtext('passportnumber')
                    guest_element.xmlSource = tostring(guest_node)
                    guest_element.put()
                    # logging.info(tostring(guest_node))

                    if enquiry.key() not in guest_element.enquiries:
                        guest_element.enquiries.append(enquiry.key())
                        guest_element.put()

                    # # create a client instance
                    # if enquiry.getStateName() == 'confirmed':
                    #     client = Client(clientNumber = generator.generateClientNumber(),
                    #                     surname=guest_element.surname,
                    #                     firstNames = guest_element.firstNames)
                    #     client.creator = users.get_current_user()
                    #     for language_node in \
                    #             guest_node.find('languages').findall('language'):
                    #         client.languages.append(language_node.text)
                    #     client.state = 'Confirmed'
                    #     client.identityNumber = guest_element.identifyingNumber
                    #     client.identityNumberType = 'Passport'
                    #     client.put()

                    #     # create email address and telephone for client
                    #     email = EmailAddress(parent=client,
                    #                          emailType='Other',
                    #                          email=guest_element.email)
                    #     email.container = client
                    #     email.creator = users.get_current_user()
                    #     email.put()

                    #     phone = PhoneNumber(parent=client,
                    #                         numberType='Other Number',
                    #                         number=guest_element.contactNumber) 
                    #     phone.container=client
                    #     phone.creator = users.get_current_user()
                    #     phone.put()
            else:
                # no enquiry found: send an error back
                confirm_elem = SubElement(node, 'confirmationresult')
                result_elem = SubElement(confirm_elem, 'result')

                # append the error element
                self._addErrorNode(node, '102',
                        'Enquiry element %s is not part of enquiry batch %s' \
                                                        % (refnum, collection_number))
                # return the result as xml
                return tostring(node)

        # append the result
        confirm_elem = SubElement(node, 'confirmationresult')
        result_elem = SubElement(confirm_elem, 'result')
        result_elem.text = collection_number

        # append the error element
        self._addErrorNode(node)

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
            try:
                result = self._checkAvailability(xmlroot)
            except:
                error = sys.exc_info()[1]
                logging.error('Unhandled error: %s', error)
                SubElement(xmlroot, 'confirmationresult')
                self._addErrorNode(xmlroot, code='1001', \
                                message='Seriously Unexpected and Unhandleable Error')
                result = tostring(xmlroot)

        elif action.lower() == 'confirm enquiries':
            # confirm the enquiries in the batch
            try:
                result = self._confirmEnquiries(xmlroot)
            except:
                error = sys.exc_info()[1]
                logging.error('Unhandled error: %s', error)
                SubElement(xmlroot, 'confirmationresult')
                self._addErrorNode(xmlroot, code='1001', \
                                message='Seriously Unexpected and Unhandleable Error')
                result = tostring(xmlroot)

        elif action.lower() == 'retrieve invoice':
            # retrieve invoice details for a batch
            result = retrieveinvoice.retrieveInvoice(xmlroot)

        elif action.lower() == 'generate enquiry number':
            number_element = SubElement(xmlroot, 'enquirynumber')
            number_element.text = generator.generateEnquiryNumber()
            result = tostring(xmlroot)

        elif action.lower() == 'generate collection number':
            number_element = SubElement(xmlroot, 'collectionnumber')
            number_element.text = generator.generateEnquiryCollectionNumber()
            result = tostring(xmlroot)

        else:
            # send back an error informing the public site
            # that we have no clue what it wants
            self._addErrorNode(xmlroot, '201', 'Unable to determine what to do')
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
