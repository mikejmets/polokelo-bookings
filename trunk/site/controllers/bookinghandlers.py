import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.contractedbooking \
    import CaptureContractedBooking, EditContractedBooking, DeleteContractedBooking
from controllers.bookingrequest \
    import CaptureBookingRequest, EditBookingRequest, DeleteBookingRequest
from models.bookinginfo import ContractedBooking, BookingRequest
from controllers.utils import get_authentication_urls


class ManageBookings(webapp.RequestHandler):
    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        contractedbookings = ContractedBooking.all().order('bookingNumber')
        bookingrequests = BookingRequest.all().order('referenceNumber')
        filepath = os.path.join(
            PROJECT_PATH, 'templates', 'bookings', 'managebookinginfo.html')
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'contractedbookings':contractedbookings,
                        'bookingrequests':bookingrequests,
                        'auth_url':auth_url,
                        'auth_url_text':auth_url_text
                        }))

application = webapp.WSGIApplication([
                  ('/bookings/bookinginfo', ManageBookings),
                  ('/bookings/capturecontractedbooking', CaptureContractedBooking),
                  ('/bookings/editcontractedbooking', EditContractedBooking),
                  ('/bookings/deletecontractedbooking', DeleteContractedBooking),
                  ('/bookings/capturebookingrequest', CaptureBookingRequest),
                  ('/bookings/editbookingrequest', EditBookingRequest),
                  ('/bookings/deletebookingrequest', DeleteBookingRequest),
                  ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
