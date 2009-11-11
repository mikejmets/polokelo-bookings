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
from controllers.bookingrequest \
    import CaptureBookingRequest, EditBookingRequest, DeleteBookingRequest
from models.hostinfo import Berth
from models.bookinginfo import ContractedBooking, BookingRequest
from controllers.utils import get_authentication_urls


class ManageBookings(webapp.RequestHandler):
    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        contractedbookings = ContractedBooking.all().order('bookingNumber')
        bookingrequests = BookingRequest.all().order('referenceNumber')
        results = []
        key_str = self.request.get('results')
        city = self.request.get('city')
        if not city:
            city = 'Cape Town'
        type = self.request.get('type')
        start = self.request.get('start')
        nights = self.request.get('nights')
        people = self.request.get('people')
        if key_str:
            keys = key_str.split(';')
            for key in keys:
                berth = Berth.get(key)
                results.append('%s, %s, %s, %s' % (
                  berth.bed.bedroom.venue.owner.listing_name(),
                  berth.bed.bedroom.venue.name,
                  berth.bed.bedroom.name,
                  berth.bed.bedType,
                  ))
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
                        'bookingrequests':bookingrequests,
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
      ('/bookings/capturebookingrequest', CaptureBookingRequest),
      ('/bookings/editbookingrequest', EditBookingRequest),
      ('/bookings/deletebookingrequest', DeleteBookingRequest),
      ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
