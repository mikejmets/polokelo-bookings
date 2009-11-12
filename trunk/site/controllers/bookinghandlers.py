import os
import urllib
import logging
from datetime import datetime
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.contractedbooking import \
    CaptureContractedBooking, EditContractedBooking, DeleteContractedBooking
from controllers.bookingstool import BookingsTool
from controllers.enquiry \
    import CaptureEnquiry, EditEnquiry, DeleteEnquiry
from models.hostinfo import Berth
from models.bookinginfo import ContractedBooking, Enquiry
from controllers.utils import get_authentication_urls


class ManageBookings(webapp.RequestHandler):
    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        contractedbookings = ContractedBooking.all().order('bookingNumber')
        enquiries = Enquiry.all().order('referenceNumber')
        results = []
        key_str = self.request.get('results')
        city = self.request.get('city', 'Potchefstroom')
        type = self.request.get('type', 'Family House')
        start = self.request.get('start', '2010-06-11')
        nights = self.request.get('nights', 6)
        people = self.request.get('people', 5)
        if key_str:
            keys = key_str.split(';')
            for key in keys:
                berth = Berth.get(key)
                results.append((
                  key,
                  berth.bed.bedroom.venue.owner.listing_name(),
                  berth.bed.bedroom.venue.name,
                  berth.bed.bedroom.name,
                  berth.bed.name,
                  berth.bed.bedType,
                  berth.bed.capacity,
                  ))
        #sort
        results.sort()

        filepath = os.path.join(
            PROJECT_PATH, 'templates', 'bookings', 'managebookinginfo.html')
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'contractedbookings':contractedbookings,
                        'city':city,
                        'type':type,
                        'start':start,
                        'nights':nights,
                        'people':people,
                        'results':results,
                        'enquiries':enquiries,
                        'auth_url':auth_url,
                        'auth_url_text':auth_url_text
                        }))

class BookingsToolFindAccommodation(webapp.RequestHandler):
    def post(self):
        tool = BookingsTool()
        came_from = '/bookings/bookinginfo' #self.request.referer
        city = self.request.get('city')
        type = self.request.get('type')
        start = self.request.get('start')
        if start:
          start = datetime.strptime(start, '%Y-%m-%d').date()
        nights = self.request.get('nights')
        if nights:
            nights = int(nights)
        people = self.request.get('people')
        if people:
            people = int(people)
        berths = tool.findBerths(city, type, start, nights, people)
        params = {}
        if berths:
            berths = [str(k) for k,v in tool.findBerths(city, type, start, nights, people)]
            berths = ';'.join(berths)
            params['results'] = berths 
        params['city'] = city
        params['type'] = type
        params['start'] = start
        params['nights'] = nights
        params['people'] = people
        params = urllib.urlencode(params)
        self.redirect("%s?%s" % (came_from, params))

application = webapp.WSGIApplication([
      ('/bookings/bookinginfo', ManageBookings),
      ('/bookings/findaccommodation', BookingsToolFindAccommodation),
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
