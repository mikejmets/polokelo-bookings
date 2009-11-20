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
from controllers.bookingstool import BookingsTool
from models.codelookup import getItemDescription


class ExternalBookings(webapp.RequestHandler):
    """ Handler class for all enquiry/booking requests from
        the pulic sites.
    """

    def _checkAvailability(self, node):
        """ Handle the initial check for available slots on an enquiry
        """
        # get the tool we query for availability
        bt = BookingsTool()

        # check the enquiry for availability
        enquiry_number = node.findtext('enquirynumber') 
        guest_email = node.findtext('email')
        agent_code = node.findtext('guestagentcode')
        city = getItemDescription(node.findtext('city')) 
        accom_type = getItemDescription( \
                        node.findtext('accommodationtype'))
        start_date = datetime.strptime(node.findtext('startdate'), 
                                        '%Y-%m-%d').date()
        duration = int(node.findtext('duration'))
        gender_sensitive = node.findtext('guestgendersensitive') == 'yes'
        adults = node.find('adults')
        adult_male = int(adults.findtext('male'))
        adult_female = int(adults.findtext('female'))
        children = node.find('adults')
        children_male = int(children.findtext('male'))
        children_female = int(children.findtext('female'))
        disability = node.find('disability')
        wheelchair = disability.findtext('wheelchairaccess') == 'yes'
        specialneeds = disability.findtext('otherspecialneeds') == 'yes'

        # do the availability check
        available, amount, expiry = bt.checkAvailability(
                enquiry_number, guest_email,
                city, accom_type, 
                start_date, duration,
                gender_sensitive,
                adult_male, adult_female,
                children_male, children_female,
                wheelchair, specialneeds)
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


    # def _findBooking(self, node):
    #     """ store the booking as temporary to enable a 
    #         staff member to do a manual allocation
    #     """
    #     # look for all the bookings in the request
    #     bookings = node.findall('booking')
    #     result = ""

    #     # get the tool we query for availability
    #     bt = BookingsTool()

    #     # create a client and temporary booking from each enquiry
    #     for booking in bookings:
    #         guestnodes = booking.find('guests')
    #         if guestnodes:
    #             primaryguest = guestnodes.find('guest')
    #             if primaryguest:
    #                 guest_key_name = booking.findtext('bookingnumber').strip().lower() + \
    #                         '-' + primaryguest.findtext('passportnumber').strip().lower()
    #                 guest = Client.find_or_insert(guest_key_name)
    #                 guest.clientNumber = 'unassigned'
    #                 guest.surname = primaryguest.findtext('surname').strip() 
    #                 guest.firstNames = primaryguest.findtext('')


    #         client = Client.get_or_insert(
    #         available = bt.checkAvailability( \
    #             booking.findtext('city'), 
    #             booking.findtext('accommodationtype'),
    #             datetime.strptime(booking.findtext('bookingdate'), '%Y-%m-%d').date(),
    #             int(booking.findtext('duration')),
    #             int(booking.findtext('numadults')) + \
    #                     int(booking.findtext('numchildren')) + \
    #                     int(booking.findtext('numinfants'))) \
    #                             and 'available' or 'not available'

    #         # append the result as a sub element to the booking element
    #         avail_elem = SubElement(booking, 'availability')
    #         avail_elem.text = available

    #     # return the result as xml
    #     return tostring(node)



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

        # if action.lower() == 'find booking':
        #     # if 'check availability' returned 'not available' 
        #     # for a booking then find a booking manually
        #     result = self._findBooking(xmlroot)

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
