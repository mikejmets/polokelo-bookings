import os
import urllib
import logging
from datetime import datetime
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.utils import get_authentication_urls
from controllers.contractedbooking import \
    AssignClientToBooking, \
    ViewContractedBooking, CaptureContractedBooking, \
    EditContractedBooking, DeleteContractedBooking
from controllers.bookingstool import BookingsTool
from controllers.enquiry \
    import CaptureEnquiry, EditEnquiry, DeleteEnquiry
from models.hostinfo import Berth
from models.bookinginfo import ContractedBooking, Enquiry, AccommodationElement
from models.codelookup import getChoices

from controllers.utils import get_authentication_urls

logger = logging.getLogger('BookingHandlers')

class ManageBookings(webapp.RequestHandler):
    def get(self):
        cityList = getChoices('CTY')
        accommodationTypes = getChoices('ACTYP')
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
            genderSensitive = element.genderSensitive
            adultMales = element.adultMales
            adultFemales = element.adultFemales
            childMales = element.childMales
            childFemales = element.childFemales
            if element.availableBerths:
                for key, slots in eval(element.availableBerths):
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
            type =  self.request.get('type', 'Family Home')
            start = self.request.get('start', '2010-06-01')
            nights = self.request.get('nights', 2)
            genderSensitive = \
                self.request.get('genderSensitive', 'False') != 'False'
            adultMales = self.request.get('adultMales', 2)
            adultFemales = self.request.get('adultFemales', 2)
            childMales = self.request.get('childMales', 0)
            childFemales = self.request.get('childFemales', 0)
        #sort
        results.sort()

        filepath = os.path.join(
            PROJECT_PATH, 'templates', 'bookings', 'managebookinginfo.html')
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'elementkey':elementkey,
                        'cities':cityList,
                        'city':city,
                        'accomtypes':accommodationTypes,
                        'type':type,
                        'start':start,
                        'nights':nights,
                        'genderSensitive':genderSensitive,
                        'adultMales':adultMales,
                        'adultFemales':adultFemales,
                        'childMales':childMales,
                        'childFemales':childFemales,
                        'results':results,
                        'contractedbookings':contractedbookings,
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
        genderSensitive = \
            self.request.get('genderSensitive', 'False') != 'False'
        adultMales = int(self.request.get('adultMales', "0"))
        adultFemales = int(self.request.get('adultFemales', "0"))
        childMales = int(self.request.get('childMales', "0"))
        childFemales = int(self.request.get('childFemales', "0"))
        #Generate number
        enquiry = Enquiry(referenceNumber='123')
        enquiry.put()
        accom_element = AccommodationElement(
            enquiry=enquiry,
            city=city,
            type=type,
            start=start,
            nights=nights,
            genderSensitive=genderSensitive,
            adultMales=adultMales,
            adultFemales=adultFemales,
            childMales=childMales,
            childFemales=childFemales,
            )
        accom_element.put()

        berths = tool.findBerths(accom_element)
        params = {}
        params['city'] = city 
        params['type'] = type
        params['start'] = start
        params['nights'] = nights
        params['genderSensitive'] = genderSensitive
        params['adultMales'] = adultMales
        params['adultFemales'] = adultFemales
        params['childMales'] = childMales
        params['childFemales'] = childFemales
        if berths:
            accom_element.availableBerths = str(berths)
            accom_element.put()
            params['elementkey'] = accom_element.key() 
            params = urllib.urlencode(params)
            self.redirect('%s?%s' % (came_from, params))
        else:
            #Clean up
            enquiry.rdelete()
            params['error'] = "No results found" 
            params = urllib.urlencode(params)
            self.redirect('/bookings/bookingerror?%s' % params)

class BookingsToolReserveAccommodation(webapp.RequestHandler):
    def post(self):
        args = self.request.arguments()
        elementkey = self.request.get('elementkey') 
        error = None
        if elementkey:
            element = AccommodationElement.get(elementkey)
            if element and element.availableBerths:
                enquiry=element.enquiry
                berthkeys = []
                for arg in args:
                    if arg.startswith('berth_'):
                        berthkey = arg[6:]
                        berthkeys.append(berthkey)
                if berthkeys:
                    tool = BookingsTool()
                    error = tool.createBookings(enquiry, element, berthkeys)
                else:
                    error = "No berths selected"

        params = {}
        params['city'] =  self.request.get('city')
        params['type'] =  self.request.get('type')
        params['start'] = self.request.get('start')
        params['nights'] = self.request.get('nights')
        params['genderSensitive'] = \
            self.request.get('genderSensitive', 'False') != 'False'
        params['adultMales'] = self.request.get('adultMales')
        params['adultFemales'] = self.request.get('adultFemales')
        params['childMales'] = self.request.get('childMales')
        params['childFemales'] = self.request.get('childFemales')
        if error:
            #Clean up
            enquiry.rdelete()
            params['error'] = error 
            params = urllib.urlencode(params)
            self.redirect('/bookings/bookingerror?%s' % params)
        else:
            params = urllib.urlencode(params)
            self.redirect('/bookings/bookinginfo?%s' % params)

class BookingError(webapp.RequestHandler):
    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        error =  self.request.get('error')
        city =  self.request.get('city')
        type =  self.request.get('type')
        start = self.request.get('start')
        nights = self.request.get('nights')
        genderSensitive = \
            self.request.get('genderSensitive', 'False') != 'False'
        adultMales = self.request.get('adultMales')
        adultFemales= self.request.get('adultFemales')
        childMales = self.request.get('childMales')
        childFemales = self.request.get('childFemales')

        filepath = os.path.join(
            PROJECT_PATH, 'templates', 'bookings', 'bookingerror.html')
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'error':error,
                        'city':city,
                        'type':type,
                        'start':start,
                        'nights':nights,
                        'genderSensitive':genderSensitive,
                        'adultMales':adultMales,
                        'adultFemales':adultFemales,
                        'childMales':childMales,
                        'childFemales':childFemales,
                        'auth_url':auth_url,
                        'auth_url_text':auth_url_text
                        }))

    def post(self):
        came_from = '/bookings/bookinginfo' 
        params = {}
        params['city'] =  self.request.get('city')
        params['type'] =  self.request.get('type')
        params['start'] = self.request.get('start')
        params['nights'] = self.request.get('nights')
        params['genderSensitive'] = self.request.get('genderSensitive')
        params['adultMales'] = self.request.get('adultMales')
        params['adultFemales'] = self.request.get('adultFemales')
        params['childMales'] = self.request.get('childMales')
        params['childFemales'] = self.request.get('childFemales')
        params = urllib.urlencode(params)
        self.redirect('%s?%s' % (came_from, params))


application = webapp.WSGIApplication([
      ('/bookings/bookinginfo', ManageBookings),
      ('/bookings/bookingerror', BookingError),
      ('/bookings/assignclient', AssignClientToBooking),
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
