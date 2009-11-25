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
from controllers.enquiry import \
    ViewEnquiry, AdvanceEnquiry, \
    CaptureEnquiry, EditEnquiry, DeleteEnquiry
from models.hostinfo import Berth
from models.bookinginfo import ContractedBooking, Enquiry, AccommodationElement
from models.codelookup import getChoices

from controllers import generator
from controllers.utils import get_authentication_urls
from workflow.__init__ import ENQUIRY_WORKFLOW

logger = logging.getLogger('BookingHandlers')

class ManageBookings(webapp.RequestHandler):
    def get(self):
        cityList = getChoices('CTY')
        accommodationTypes = getChoices('ACTYP')
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        contractedbookings = ContractedBooking.all().order('bookingNumber')
        enquiries = Enquiry.all().order('referenceNumber')
        berths = []
        elementkey = self.request.get('elementkey')
        if elementkey:
            element = AccommodationElement.get(elementkey)
            city = element.city
            type = element.type
            start = element.start
            nights = element.nights
            wheelchairAccess = element.wheelchairAccess
            adults = element.adults
            children = element.children
            if element.availableBerths:
                for key, slots in eval(element.availableBerths):
                    berth = Berth.get(key)
                    berths.append(berth)
            if berths:
                #sort
                berths.sort(key=lambda x: "%s %s %s %s" % (
                    x.bed.bedroom.venue.owner.listing_name(),
                    x.bed.bedroom.venue.name,
                    x.bed.bedroom.name,
                    x.bed.name))
        else:
            city =  self.request.get('city', 'Potchefstroom')
            type =  self.request.get('type', 'Family Home')
            start = self.request.get('start', '2010-06-01')
            nights = self.request.get('nights', 2)
            wheelchairAccess = \
                self.request.get('wheelchairAccess', 'off') != 'off'
            adults = self.request.get('adults', 2)
            children = self.request.get('children', 0)

        filepath = os.path.join(
            PROJECT_PATH, 'templates', 'bookings', 'managebookinginfo.html')
        extras = {'base_path':BASE_PATH,
                  'elementkey':elementkey,
                  'cities':cityList,
                  'city':city,
                  'accomtypes':accommodationTypes,
                  'type':type,
                  'start':start,
                  'nights':nights,
                  'adults':adults,
                  'children':children,
                  'berths':berths,
                  'contractedbookings':contractedbookings,
                  'enquiries':enquiries,
                  'auth_url':auth_url,
                  'auth_url_text':auth_url_text
                  }
        if wheelchairAccess:
            extras['wheelchairAccess'] = 'on'

        self.response.out.write(template.render(filepath, extras))


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
        wheelchairAccess = \
            self.request.get('wheelchairAccess', 'off') != 'off'
        adults = int(self.request.get('adults', "0"))
        children = int(self.request.get('children', "0"))
        #Generate number
        ref_num = generator.generateEnquiryNumber()
        enquiry = Enquiry(referenceNumber=ref_num)
        enquiry.put()
        enquiry.enterWorkflow(ENQUIRY_WORKFLOW)
        accom_element = AccommodationElement(
            parent=enquiry,
            city=city,
            type=type,
            start=start,
            nights=nights,
            wheelchairAccess=wheelchairAccess,
            adults=adults,
            children=children,
            )
        accom_element.put()

        berths = tool.findBerths(accom_element)
        params = {}
        params['city'] = city 
        params['type'] = type
        params['start'] = start
        params['nights'] = nights
        if wheelchairAccess:
            params['wheelchairAccess'] = 'on'
        params['adults'] = adults
        params['children'] = children
        if berths:
            accom_element.availableBerths = str(berths)
            accom_element.put()
            params['elementkey'] = accom_element.key() 
            params = urllib.urlencode(params)
            self.redirect('%s?%s' % (came_from, params))
        else:
            #Clean up
            enquiry.doTransition('assigntouser')
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
                enquiry=element.parent()
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
        if self.request.get('wheelchairAccess', 'off') != 'off':
            params['wheelchairAccess'] = 'on'
        params['adults'] = self.request.get('adults')
        params['children'] = self.request.get('children')
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
        wheelchairAccess = \
            self.request.get('wheelchairAccess', 'off') != 'off'
        adults = self.request.get('adults')
        children = self.request.get('children')

        filepath = os.path.join(
            PROJECT_PATH, 'templates', 'bookings', 'bookingerror.html')
        extras= { 'base_path':BASE_PATH,
                  'error':error,
                  'city':city,
                  'type':type,
                  'start':start,
                  'nights':nights,
                  'adults':adults,
                  'children':children,
                  'auth_url':auth_url,
                  'auth_url_text':auth_url_text
                  }
        if wheelchairAccess:
            extras['wheelchairAccess'] = 'on'

        self.response.out.write(
            template.render(filepath, extras))

    def post(self):
        came_from = '/bookings/bookinginfo' 
        params = {}
        params['city'] =  self.request.get('city')
        params['type'] =  self.request.get('type')
        params['start'] = self.request.get('start')
        params['nights'] = self.request.get('nights')
        if self.request.get('wheelchairAccess', 'off') != 'off':
            params['wheelchairAccess'] = 'on'
        params['adults'] = self.request.get('adults')
        params['children'] = self.request.get('children')
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
      ('/bookings/enquiry/viewenquiry', ViewEnquiry),
      ('/bookings/enquiry/advanceenquiry', AdvanceEnquiry),
      ('/bookings/enquiry/captureenquiry', CaptureEnquiry),
      ('/bookings/enquiry/editenquiry', EditEnquiry),
      ('/bookings/enquiry/deleteenquiry', DeleteEnquiry),
      ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
