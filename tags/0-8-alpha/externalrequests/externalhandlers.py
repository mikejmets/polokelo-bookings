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
from controllers.bookingstool import BookingsTool


class ExternalBookings(webapp.RequestHandler):

    def _checkAvailability(self, node):
        bookings = node.findall('booking')
        result = ""
        bt = BookingsTool()

        for booking in bookings:
            available = bt.checkAvailability( \
                booking.findtext('city'), 
                booking.findtext('accommodationtype'),
                datetime.strptime(booking.findtext('bookingdate'), '%Y-%m-%d').date(),
                int(booking.findtext('duration')),
                int(booking.findtext('numadults')) + \
                        int(booking.findtext('numchildren')) + \
                        int(booking.findtext('numinfants'))) \
                                and 'available' or 'not available'

            avail_elem = SubElement(booking, 'availability')
            avail_elem.text = available

        return tostring(node)

    def post(self):
        xml = self.request.body
        logging.info(xml)

        # find out what to do
        xmlroot = XML(xml)
        action = xmlroot.findtext('action')
        if action.lower() == 'check availability':
            result = self._checkAvailability(xmlroot)
        else:
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
