import os
import logging
import urllib
from datetime import datetime, timedelta

from google.appengine.ext import webapp
from google.appengine.ext.db import run_in_transaction
from google.appengine.ext.webapp import template

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.utils import get_authentication_urls
from booking_errors import BookingConflictError
from models.hostinfo import Slot, Berth
from models.bookinginfo import \
    ContractedBooking, Enquiry, AccommodationElement

logger = logging.getLogger('BookingsTool')

class BookingsTool():

  def checkAvailability(self, city, type, start, nights, people):
      return len(self.findBerths(city, type, start, nights, people)) > 0

  def findVenues(self, city, type, start, nights, people):
      berths = self.findBerths(city, type, start, nights, people)
      venues = set()
      for key, slots in berths:
          venues.add(Berth.get(key).bed.bedroom.venue.name)
      return venues

  def findBerths(self, city, type, start, nights, people):
        logger.info('Search for %s, %s, %s(%s), %s', \
            city, type, start, nights, people)
        berths = self.findValidBerths(city, type, start, nights)

        #for key, slots in berths:
        #  logger.info('valid pairing %s: %s', key, slots)
        if len(berths) >= people:
            logger.info('Found %s pairings for %s people', 
                len(berths), people)
            return berths
        else:
            logger.info('Sorry, only found %s pairings for %s people', 
                len(berths), people)
            return []

  def findValidBerths(self, city, type, start, nights):
        end = start + timedelta(days = (nights-1))
        #logger.info('Search for %s, %s, %s -> %s(%s)', \
        #    city, type, start, end, nights)

        slots = Slot.all()
        slots.filter('occupied =', False)
        slots.filter('city =', city)
        slots.filter('type =', type)
        slots.filter('startDate >=', start)
        slots.filter('startDate <=', end)
        slots.order('startDate')

        #group by berth
        berths = {}
        for slot in slots:
            #logger.info('Found berth %s', slot.berth.key())
            berthkey = str(slot.berth.key())
            if berths.has_key(berthkey):
                berths[berthkey]['slots'].append(str(slot.key()))
            else:
                berths[berthkey] = {'slots': [str(slot.key())], 'valid':False}
        #check for complete 
        for key in berths.keys():
            #logger.info('Check pair %s', key)
            valid = True #until proven otherwise
            #Check completeness
            if len(berths[key]['slots']) != nights:
                logger.info('INVALID: Pairing for %s is incomplete', key)
                break #it remains false
            if valid:
                berths[key]['valid'] = True
                
        valid_berths = []
        for key in berths.keys():
            #logger.info('Valid pairing %s', berths[key]['valid'])
            if berths[key]['valid']:
                valid_berths.append((key, berths[key]['slots']))

        #for key, slots in valid_berths:
        # logger.info('valid pairing %s: %s', key, slots)

        return valid_berths


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
        #Generate number
        enquiry = Enquiry(referenceNumber='123')
        enquiry.put()
        accom_element = AccommodationElement(
            enquiry=enquiry,
            city=city,
            type=type,
            start=start,
            nights=nights,
            people=people)
        accom_element.put()

        berths = tool.findBerths(city, type, start, nights, people)
        params = {}
        params['city'] =  self.request.get('city')
        params['type'] =  self.request.get('type')
        params['start'] = self.request.get('start')
        params['nights'] = self.request.get('nights')
        params['people'] = self.request.get('people')
        if berths:
            accom_element.available_berths = str(berths)
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
            if element and element.available_berths:
                enquiry=element.enquiry
                berthkeys = []
                for arg in args:
                    if arg.startswith('berth_'):
                        berthkey = arg.split('_')[-1]
                        berthkeys.append(berthkey)
                if berthkeys:
                    error = self._createBookings(enquiry, element, berthkeys)
                else:
                    error = "No berths selected"

        params = {}
        params['city'] =  self.request.get('city')
        params['type'] =  self.request.get('type')
        params['start'] = self.request.get('start')
        params['nights'] = self.request.get('nights')
        params['people'] = self.request.get('people')
        if error:
            #Clean up
            enquiry.rdelete()
            params['error'] = error 
            params = urllib.urlencode(params)
            self.redirect('/bookings/bookingerror?%s' % params)
        else:
            params = urllib.urlencode(params)
            self.redirect('/bookings/bookinginfo?%s' % params)

    def _createBookings(self, enquiry, element, berthkeys):
        #Mark slots as occupied
        error = None
        bookings = []
        try:
            people = 0
            for berthkey, slotkeys in eval(element.available_berths):
                if berthkey in berthkeys:
                    #Create Booking
                    booking = ContractedBooking(
                        bookingNumber='123',
                        enquiry=enquiry,
                        duration=element.nights)
                    booking.put()
                    bookings.append(booking)
                    logger.error("Create booking: %s", booking) 
                    people += 1
                    run_in_transaction(
                        self._assignBookingToSlots, 
                        enquiry, 
                        slotkeys, 
                        booking)
            if people:
                enquiry.state = 'inprocess'
                enquiry.put()
        except BookingConflictError, error:
            logger.error("BookingConflict: %s", error) 
            #Clean up
            for booking in bookings:
                booking.rdelete()

        return error

    def _assignBookingToSlots(self, enquiry, slotkeys, booking):
        for slotkey in slotkeys:
            slot = Slot.get(slotkey) 
            if slot.occupied == False:
                slot.occupied = True
                slot.contracted_booking = booking
                slot.put()
            else:
                logger.info(
                  'LOGGER Conflict on enquiry %s (bed %s, date %s)' \
                      % (enquiry.referenceNumber,
                         slot.berth.bed.name,
                         slot.startDate))
                raise BookingConflictError(
                  'Conflict on enquiry %s (bed %s, date %s)' \
                      % (enquiry.referenceNumber,
                         slot.berth.bed.name,
                         slot.startDate))
                  #'Conflict on enquiry %s (owner %s, venue %s, room %s, bed %s, date %s)' \
                  #    % (enquiry.referenceNumber,
                  #       slot.berth.bed.bedroom.venue.owner.surname,
                  #       slot.berth.bed.bedroom.venue.name,
                  #       slot.berth.bed.bedroom.name,
                  #       slot.berth.bed.name,
                  #       slot.startDate))

class BookingError(webapp.RequestHandler):
    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        error =  self.request.get('error')
        city =  self.request.get('city')
        type =  self.request.get('type')
        start = self.request.get('start')
        nights = self.request.get('nights')
        people = self.request.get('people')

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
                        'people':people,
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
        params['people'] = self.request.get('people')
        params = urllib.urlencode(params)
        self.redirect('%s?%s' % (came_from, params))
