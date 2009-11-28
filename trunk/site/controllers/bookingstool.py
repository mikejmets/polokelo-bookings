import os
import logging
import urllib
from datetime import datetime, timedelta

from google.appengine.ext.db import run_in_transaction

from booking_errors import BookingConflictError
from models.hostinfo import Slot, Berth
from models.bookinginfo import \
    ContractedBooking, Enquiry, AccommodationElement
from models.packages import Package
from controllers import generator

logger = logging.getLogger('BookingsTool')

class BookingsTool():

    def checkAvailability(self, enquiry):
        """ check for availabilty for the given accommodation element
            used from the public sites to do initial enquiries
        """
        #Defaults
        quote_amount = 0.0
        vat_amount = 0.0

        #search
        query = AccommodationElement.all().ancestor(enquiry)
        #accommodationElement = query.fetch(1)[0]
        accommodationElement = query.get()
        logger.info("Got element %s", accommodationElement)

        # check for scpecial needs and return
        if accommodationElement.specialNeeds == True:
            logger.info("specialneeds is %s", accommodationElement.specialNeeds)
            # SHOULD WE TRANSITION TO MANUAL???
            return (False, 0.0, 0.0)

        # Check if we have a package for the accommodation type in the city.
        # This indicates contracted bookings of the type are available
        #   and auto allocation and quote can go ahead.
        query = Package.all()
        query.filter('city =', accommodationElement.city)
        query.filter('accommodationType =', accommodationElement.type)
        package = query.get()
        if not package:
            logger.info('No package found')
            return (False, 0.0, 0.0)

        logging.info('Package: %s, %s, %5.2f', \
                                package.city, package.accommodationType, 
                                package.basePriceInZAR)

        # now, carry on and look for availble accommodation
        venues = self.findVenues(accommodationElement) 
        if venues:
            accommodationElement.availableBerths = str(venues)
            #Simply pull from the top of the list
            quote_amount, vat_amount = package.calculateQuote(accommodationElement)
            selected_venue = venues[venues.keys()[0]]
            people = accommodationElement.adults + \
                     accommodationElement.children 
            selected_berths = [b[0] for b in selected_venue[:people]]
            self.createBookings(enquiry,
                              accommodationElement,
                              selected_berths)
            return (True, quote_amount, vat_amount)

        return (False, 0.0, 0.0)


    def findVenues(self, element):
        h1 = SimpleAccommodationSearch()
        
        return h1.findVenues(element)


    def createBookings(self, enquiry, element, selected_keys):
        #Mark slots as occupied
        error = None
        bookings = []
        try:
            people = 0
            #logger.info('AvailableBerths: %s', element.availableBerths)
            venues = eval(element.availableBerths)
            for venue_key in venues.keys():
                for berth_key, slotkeys in venues[venue_key]:
                    if berth_key in selected_keys:
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
                if enquiry.workflowState == 'requiresintervention':
                    enquiry.doTransition('allocatemanually')
                else:
                    enquiry.doTransition('allocate')
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
                raise BookingConflictError(
                    'Conflict on enquiry %s (bed %s, date %s): bed taken after search' \
                      % (enquiry.referenceNumber,
                         slot.berth.bed.name,
                         slot.startDate))


class AccommodationSearch():
    successor = None

    #this is always subclassed
    def findVenues(self, element):
        logger.error('AccommodationSearch.findVenues should always subclassed')
        return {}

    def searchNext(self, element):
        if self.successor:
            return self.successor.findVenues(element)
        else:
            return {}

    def _validateBerths(self, slots, element):
        #Group slots by berth in a dict
        venues = {}
        for slot in slots:
            #logger.info('Found berth %s', slot.berth.key())
            venue_key = str(slot.berth.bed.bedroom.venue.key())
            berth_key = str(slot.berth.key())
            if not venues.has_key(venue_key):
                venues[venue_key] = {}
            venue = venues[venue_key]
            if venue.has_key(berth_key):
                venue[berth_key].append(str(slot.key()))
            else:
                venue[berth_key] = [str(slot.key())]

        #Check for completeness
        valid_venues = {}
        for venue_key in venues.keys():
            venue = venues[venue_key]
            valid_berths = []
            for berth_key in venue.keys():
                berth = venue[berth_key]
                #Check completeness
                if len(berth) != element.nights:
                    #logger.info('INVALID: Pairing for %s is incomplete', key)
                    break #it remains false
                valid_berths.append((berth_key, berth))
            if len(valid_berths) > 0:
                valid_venues[venue_key] = valid_berths
                
        #for key, slots in valid_berths:
        # logger.info('valid pairing %s: %s', key, slots)
        return valid_venues

class SimpleAccommodationSearch(AccommodationSearch):

    def findVenues(self, element):
        logger.info('SimpleAccommodationSearch for %s, %s, %s(%s)', 
            element.city, element.type, element.start, element.nights)

        venues = self._findValidBerths(element)

        #for key, slots in berths:
        #  logger.info('valid pairing %s: %s', key, slots)

        #Find venues with enough berths for all people
        people = element.adults + element.children
        venue_keys = venues.keys()
        valid_venues = {}
        if len(venue_keys) > 0:
            for venue_key in venue_keys:
                berths = venues[venue_key]
                if len(berths) >= people:
                    valid_venues[venue_key] = berths
        if valid_venues:
            logger.info('Found %s venues for %s people', 
                len(valid_venues.keys()), people)
            return valid_venues

        logger.info('SimpleSearch unsuccessful')
        return self.searchNext(element)

    def _findValidBerths(self, element):
        #Infer extra criteria
        end = element.start + timedelta(days = (element.nights-1))
        child_friendly_required = element.children > 0
        #logger.info('Search for %s, %s, %s -> %s(%s), %s', 
        #  element.city, element.type, element.start, end, element.nights,
        #  child_friendly_required)

        #Contract query
        slots = Slot.all()
        slots.filter('occupied =', False)
        slots.filter('city =', element.city)
        slots.filter('venueType =', element.type)
        if element.wheelchairAccess:
            slots.filter('wheelchairAccess =', True)
        if child_friendly_required:
            slots.filter('childFriendly =', True)
        slots.filter('startDate >=', element.start)
        slots.filter('startDate <=', end)
        slots.order('startDate')

        #Run query and 
        return self._validateBerths(slots, element)



