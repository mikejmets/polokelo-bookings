import os
import logging
import urllib
from datetime import datetime, timedelta

from google.appengine.ext.db import run_in_transaction

from booking_errors import BookingConflictError
from models.hostinfo import Slot, Berth
from models.bookinginfo import \
    ContractedBooking, Enquiry, AccommodationElement
from controllers import generator

logger = logging.getLogger('BookingsTool')

class BookingsTool():

    def checkAvailability(self, enquiry):
        """ check for availabilty for the given accommodation element
            used from the public sites to do initial enquiries
        """
        #Defaults
        quote_amount = 0.0
        expiry_date = datetime.now()

        #search
        query = AccommodationElement.all().ancestor(enquiry)
        accommodationElement = query.fetch(1)[0]
        logger.info("Got element %s", accommodationElement)

        berths = self.findBerths(accommodationElement) 
        if berths:
          accommodationElement.availableBerths = str(berths)
          #Simply pull from the top of the list
          people = accommodationElement.adults + \
                   accommodationElement.children 
          if people <= len(berths): #Should always be true
              quote_amount = self.calculateQuote(accommodationElement)
              expiry_date = datetime.now() + timedelta(minutes=30)
              selected_berths = [b[0] for b in berths[:people]]
              self.createBookings(enquiry,
                                  accommodationElement,
                                  selected_berths)
        return (len(berths) > 0, quote_amount, expiry_date)


    def calculateQuote(self, accommodationElement):
        """ calculate the quote for the enquiry based on the packages
        """
        # we do not have package info yet, so just return something
        return 5555.55

    def findBerths(self, element):
        h1 = SimpleAccommodationSearch()
        h2 = WheelchairAccommodationSearch()
        h1.successor = h2
        
        return h1.findBerths(element)


    def createBookings(self, enquiry, element, berthkeys):
        #Mark slots as occupied
        error = None
        bookings = []
        try:
            people = 0
            #logger.info('AvailableBerths: %s', element.availableBerths)
            for berthkey, slotkeys in eval(element.availableBerths):
                if berthkey in berthkeys:
                    #Create Booking
                    booking = ContractedBooking(
                        bookingNumber=generator.generateBookingNumber(),
                        enquiry=enquiry)
                    booking.put()
                    bookings.append(booking)
                    logger.info('Create booking: %s', booking.bookingNumber) 
                    people += 1
                    run_in_transaction(
                        self._assignBookingToSlots, 
                        enquiry, 
                        slotkeys, 
                        booking)
            if people:
                enquiry.do_trans('allocate')
                enquiry.put()
        except BookingConflictError, error:
            logger.error('BookingConflict: %s', error) 
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
                #logger.info(
                #  'LOGGER Conflict on enquiry %s (bed %s, date %s)' \
                #      % (enquiry.referenceNumber,
                #         slot.berth.bed.name,
                #         slot.startDate))
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


class AccommodationSearch():
    successor = None

    #this is always subclassed
    def findBerths(self, element):
        logger.error('AccommodationSearch.findBerths should always subclassed')
        return []

    def searchNext(self, element):
        if self.successor:
            return self.successor.findBerths(element)
        else:
            return []

class SimpleAccommodationSearch(AccommodationSearch):

    def findBerths(self, element):
        logger.info('SimpleAccommodationSearch for %s, %s, %s(%s)', 
            element.city, element.type, element.start, element.nights)

        if element.wheelchairAccess:
            return self.searchNext(element)

        berths = self._findValidBerths(element)

        #for key, slots in berths:
        #  logger.info('valid pairing %s: %s', key, slots)
        people = element.adults + element.children
        if len(berths) >= people:
            logger.info('Found %s simple pairings for %s people', 
                len(berths), people)
            return berths
        else:
            logger.info('SimpleSearch unsuccessful')
            return self.searchNext(element)

    def _findValidBerths(self, element):
        end = element.start + timedelta(days = (element.nights-1))
        #logger.info('Search for %s, %s, %s -> %s(%s)', \
        # element.city, element.type, element.start, end, element.nights)

        slots = Slot.all()
        slots.filter('occupied =', False)
        slots.filter('city =', element.city)
        slots.filter('type =', element.type)
        slots.filter('startDate >=', element.start)
        slots.filter('startDate <=', end)
        slots.order('startDate')

        #Hack for logging
        #getslotsforlogger = [s for s in slots]
        #logger.info('Found %s slots', len(getslotsforlogger))

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
            if len(berths[key]['slots']) != element.nights:
                #logger.info('INVALID: Pairing for %s is incomplete', key)
                break #it remains false
            if valid:
                berths[key]['valid'] = True
                
        valid_berths = []
        for key in berths.keys():
            if berths[key]['valid']:
                #logger.info('Valid pairing %s %s', key, berths[key]['slots'])
                valid_berths.append((key, berths[key]['slots']))

        #for key, slots in valid_berths:
        # logger.info('valid pairing %s: %s', key, slots)
        return valid_berths

class WheelchairAccommodationSearch(AccommodationSearch):

    def findBerths(self, element):
        logger.info('WheelchairAccommodationSearch for %s, %s, %s(%s)', 
            element.city, element.type, element.start, 
            element.nights)

        if not element.wheelchairAccess:
            return self.searchNext(element)

        berths = self._findValidBerths(element)

        #for key, slots in berths:
        #  logger.info('valid pairing %s: %s', key, slots)
        people = element.adults + element.children
        if len(berths) >= people:
            logger.info('Found %s wheelchair pairings for %s people', 
                len(berths), people)
            return berths
        else:
            logger.info('WheelchairAccommodationSearch unsuccessful')
            return self.searchNext(element)

    def _findValidBerths(self, element):
        end = element.start + timedelta(days = (element.nights-1))
        #logger.info('Search for %s, %s, %s -> %s(%s)', \
        # element.city, element.type, element.start, end, element.nights)

        slots = Slot.all()
        slots.filter('occupied =', False)
        slots.filter('wheelchairAccess =', True)
        slots.filter('city =', element.city)
        slots.filter('type =', element.type)
        slots.filter('startDate >=', element.start)
        slots.filter('startDate <=', end)
        slots.order('startDate')

        #Hack for logging
        #getslotsforlogger = [s for s in slots]
        #logger.info('Found %s slots', len(getslotsforlogger))

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
            if len(berths[key]['slots']) != element.nights:
                #logger.info('INVALID: Pairing for %s is incomplete', key)
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

