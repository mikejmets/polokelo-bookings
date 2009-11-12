import os
import urllib
import logging
from datetime import datetime
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.contractedbooking import \
    ViewContractedBooking, CaptureContractedBooking, \
    EditContractedBooking, DeleteContractedBooking
from controllers.bookingstool import \
    BookingsTool, BookingsToolReserveAccommodation, \
    BookingsToolFindAccommodation
from controllers.enquiry \
    import CaptureEnquiry, EditEnquiry, DeleteEnquiry
from models.hostinfo import Berth
from models.bookinginfo import ContractedBooking, Enquiry, AccommodationElement
from controllers.utils import get_authentication_urls

logger = logging.getLogger('BookingHandlers')

class ManageBookings(webapp.RequestHandler):
    def get(self):
        people = self.request.get('people', 'zip')
        logger.info('----------%s', people)
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        contractedbookings = ContractedBooking.all().order('bookingNumber')
        enquiries = Enquiry.all().order('referenceNumber')
        results = []
        elementkey = self.request.get('elementkey')
        if elementkey:
            element = AccommodationElement.get(elementkey)
            city = element.city
            type = element.type
            start = element.start
            nights = element.nights
            people = element.people
            if element.available_berths:
                for key, slots in eval(element.available_berths):
                    berth = Berth.get(key)
                    results.append(( 
                      'berth_%s' %key,
                      berth.bed.bedroom.venue.owner.listing_name(),
                      berth.bed.bedroom.venue.name,
                      berth.bed.bedroom.name,
                      berth.bed.name,
                      berth.bed.bedType,
                      berth.bed.capacity,
                      ))
        else:
            city =  self.request.get('city', 'Potchefstroom')
            type =  self.request.get('type', 'Family House')
            start = self.request.get('start', '2010-06-11')
            nights = self.request.get('nights', 7)
            people = self.request.get('people', 5)
        #sort
        results.sort()

        filepath = os.path.join(
            PROJECT_PATH, 'templates', 'bookings', 'managebookinginfo.html')
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'elementkey':elementkey,
                        'city':city,
                        'type':type,
                        'start':start,
                        'nights':nights,
                        'people':people,
                        'results':results,
                        'contractedbookings':contractedbookings,
                        'enquiries':enquiries,
                        'auth_url':auth_url,
                        'auth_url_text':auth_url_text
                        }))


application = webapp.WSGIApplication([
      ('/bookings/bookinginfo', ManageBookings),
      ('/bookings/findaccommodation', BookingsToolFindAccommodation),
      ('/bookings/reserveaccommodation', BookingsToolReserveAccommodation),
      ('/bookings/viewcontractedbooking', ViewContractedBooking),
      ('/bookings/capturecontractedbooking', CaptureContractedBooking),
      ('/bookings/editcontractedbooking', EditContractedBooking),
      ('/bookings/deletecontractedbooking', DeleteContractedBooking),
      ('/bookings/captureenquiry', CaptureEnquiry),
      ('/bookings/editenquiry', EditEnquiry),
      ('/bookings/deleteenquiry', DeleteEnquiry),
      ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
