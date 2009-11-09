import os
import datetime
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms

from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.api import datastore_errors
from google.appengine.api import users

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.utils import get_authentication_urls

from models.bookinginfo import BookingRequest

logger = logging.getLogger('externalhandlers.py')


# class AvailabilityCheckForm(djangoforms.ModelForm):
#     class Meta:
#         model = BookingRequest
#         exclude = ['created', 'creator']
 
class CheckAvailability(webapp.RequestHandler):
 
#     def get(self):
#         auth_url, auth_url_text = get_authentication_urls(self.request.uri)
#         filepath = os.path.join(PROJECT_PATH, 'templates', 'externalrequests', 'availabilitycheck.html')
#         self.response.out.write(template.render(filepath, 
#                                     {
#                                         'form':AvailabilityCheckForm(),
#                                         'base_path':BASE_PATH,
#                                         'auth_url':auth_url,
#                                         'auth_url_text':auth_url_text
#                                         }))

    def post(self):
        referenceNumber = self.request.get('referenceNumber')
        logger.info(self.request)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n')
        self.response.out.write('<bookingrequest>\n')

        try:
            if referenceNumber:
                # booking_req = BookingRequest.get_or_insert(referenceNumber,
                #         creator = users.get_current_user(),
                #         referenceNumber = referenceNumber,
                #         city = self.request.get('city'),
                #         serviceType = self.request.get('serviceType'),
                #         startDate = datetime.datetime.strptime(self.request.get('startDate'), '%Y-%m-%d').date(),
                #         duration = int(self.request.get('duration')),
                #         quantity = int(self.request.get('quantity')),
                #         state = self.request.get('state'))
                # xml = booking_req.to_xml()

                self.response.out.write('<bookingnumber>%s</bookingnumber>\n' 
                                                % referenceNumber)
                import random
                if random.randrange(0,10) < 5:
                    self.response.out.write('<result>available</result>\n')
                else:
                    self.response.out.write('<result>not available</result>\n')
                self.response.out.write('<error />\n')
            else:
                self.response.out.write('<bookingnumber />\n')
                self.response.out.write('<result />\n')
                self.response.out.write('<error>no booking number supplied</error>\n')

        except:
            self.response.out.write('<bookingnumber />\n')
            self.response.out.write('<result />\n')
            self.response.out.write('<error>unhandled error</error>\n')

        self.response.out.write('</bookingrequest>\n')

class ExternalBookingsIndex(webapp.RequestHandler):

    def get(self):
        self.response.out.write('external bookings index page')

application = webapp.WSGIApplication([
                  ('/externalbookings/checkavailability', CheckAvailability),
                  ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
