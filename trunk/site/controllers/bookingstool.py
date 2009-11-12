import logging
import urllib
from datetime import datetime, timedelta

from google.appengine.ext import webapp
from google.appengine.ext.db import Query

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
        #  logger.info("valid pairing %s: %s", key, slots)
        if len(berths) >= people:
            logger.info("Found %s pairings for %s people", 
                len(berths), people)
            return berths
        else:
            logger.info("Sorry, only found %s pairings for %s people", 
                len(berths), people)
            return []

  def findValidBerths(self, city, type, start, nights):
        end = start + timedelta(days = (nights-1))
        #logger.info('Search for %s, %s, %s -> %s(%s)', \
        #    city, type, start, end, nights)

        query = Slot.all()
        query.filter('occupied =', False)
        query.filter('city =', city)
        query.filter('type =', type)
        query.filter('startDate >=', start)
        query.filter('startDate <=', end)
        query.order('startDate')

        slots = query.fetch(1000)
        logger.info("Found %s results", len(slots))
        #group by berth
        berths = {}
        for slot in slots:
            #logger.info("Found berth %s", slot.berth.key())
            berthkey = str(slot.berth.key())
            if berths.has_key(berthkey):
                berths[berthkey]['slots'].append(str(slot.key()))
            else:
                berths[berthkey] = {'slots': [str(slot.key())], 'valid':False}
        #check for complete 
        for key in berths.keys():
            #logger.info("Check pair %s", key)
            valid = True #until proven otherwise
            #Check completeness
            if len(berths[key]['slots']) != nights:
                logger.info("INVALID: Pairing for %s is incomplete", key)
                break #it remains false
            if valid:
                berths[key]['valid'] = True
                
        valid_berths = []
        for key in berths.keys():
            #logger.info("Valid pairing %s", berths[key]['valid'])
            if berths[key]['valid']:
                valid_berths.append((key, berths[key]['slots']))

        #for key, slots in valid_berths:
        # logger.info("valid pairing %s: %s", key, slots)

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
        if berths:
            accom_element.available_berths = str(berths)
            accom_element.put()
            params['elementkey'] = accom_element.key() 
        params = urllib.urlencode(params)
        self.redirect("%s?%s" % (came_from, params))

class BookingsToolReserveAccommodation(webapp.RequestHandler):
    def post(self):
        came_from = '/bookings/bookinginfo' #self.request.referer
        args = self.request.arguments()
        elementkey = self.request.get('elementkey') 
        if elementkey:
            element = AccommodationElement.get(elementkey)
            enquiry=element.enquiry
            if element.available_berths:
                berthkeys = []
                for arg in args:
                    if arg.startswith('berth_'):
                        berthkey = arg.split('_')[-1]
                        berthkeys.append(berthkey)
                #Create Booking
                booking = ContractedBooking(
                    bookingNumber='123',
                    enquiry=enquiry)
                booking.put()
                #Mark slots as occupied
                for berthkey, slotkeys in eval(element.available_berths):
                    if berthkey in berthkeys:
                        for slotkey in slotkeys:
                            slot = Slot.get(slotkey) 
                            slot.occupied = True
                            slot.contracted_booking = booking
                            slot.put()
            #Clean up
            if enquiry.state == 'temporary':
                enquiry.rdelete()
        params = {}
        params = urllib.urlencode(params)
        self.redirect("%s?%s" % (came_from, params))

