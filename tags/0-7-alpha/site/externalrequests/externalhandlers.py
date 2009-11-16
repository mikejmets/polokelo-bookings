import os
from datetime import datetime
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import datastore_errors
from google.appengine.api import users

from xml.etree.ElementTree import XML

from models.bookinginfo import BookingRequest
from controllers.bookingstool import BookingsTool


class ExternalBookings(webapp.RequestHandler):

    def _getAvailabilityCheckData(self, booking):
        result = {}
        result['bookingNumber'] = booking.findtext('bookingnumber')
        result['city'] = booking.findtext('city')
        result['accommodationtype'] = booking.findtext('accommodationtype')
        result['bookingdate'] = datetime.strptime(booking.findtext('bookingdate'), '%Y-%m-%d').date()
        result['duration'] = int(booking.findtext('duration'))
        result['numadults'] = int(booking.findtext('numadults'))
        result['numchildren'] = int(booking.findtext('numchildren'))
        result['numinfants'] = int(booking.findtext('numinfants'))
        logging.info(result)
        return result

    def _checkAvailability(self, node):
        bookings = node.findall('booking')
        result = ""
        for booking in bookings:
            detail = self._getAvailabilityCheckData(booking)

            bt = BookingsTool()
            available = bt.checkAvailability( \
                    detail['city'], 
                    detail['accommodationtype'],
                    detail['bookingdate'],
                    detail['duration'],
                    detail['numadults'] + detail['numchildren'] + detail['numinfants']) and 'available' or 'not available'

            result += """<booking>
<bookingnumber>%s</bookingnumber>
<result>%s</result>
</booking>
""" % (detail['bookingNumber'], available)

        return result

    def post(self):
        xml = self.request.body
        logging.info(xml)

        # find out what to do
        xmlroot = XML(xml)
        action = xmlroot.findtext('action')
        if action.lower() == 'check availability':
            result = self._checkAvailability(xmlroot)
        else:
            result = "<error>Unable to determine what to do</error>"
 
        # return the result
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('<bookingrequest>\n')
        self.response.out.write('<action>%s</action>\n' % action)
        self.response.out.write(result)
        self.response.out.write('</bookingrequest>\n')


application = webapp.WSGIApplication([
                  ('/externalbookings', ExternalBookings),
                  ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
