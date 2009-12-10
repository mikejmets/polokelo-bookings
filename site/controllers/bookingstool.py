import os
import sys
import logging
import urllib
from datetime import datetime, timedelta

from google.appengine.ext.db import run_in_transaction

from workflow.workflow import WorkflowError
from booking_errors import BookingConflictError
from models.hostinfo import Venue, Slot, Berth
from models.bookinginfo import \
    ContractedBooking, Enquiry, AccommodationElement
from models.packages import Package
from controllers import generator
from controllers.date_utils import getDateList

logger = logging.getLogger('BookingsTool')

class BookingsTool():

    def checkAvailability(self, enquiry):
        """ check for availabilty for the given accommodation element
            used from the public sites to do initial enquiries
        """
        #Defaults
        quote_amount = 0L

        #search
        query = AccommodationElement.all().ancestor(enquiry)
        #element = query.fetch(1)[0]
        element = query.get()
        logger.info("Got element %s", element)

        # check for scpecial needs and return
        if element.specialNeeds == True:
            logger.info("specialneeds is %s", element.specialNeeds)
            # SHOULD WE TRANSITION TO MANUAL???
            return (False, 0L)

        # Check if we have a package for the accommodation type in the city.
        # This indicates contracted bookings of the type are available
        #   and auto allocation and quote can go ahead.
        query = Package.all()
        query.filter('city =', element.city)
        query.filter('accommodationType =', element.type)
        package = query.get()
        if not package:
            logger.info('No package found')
            return (False, 0L)

        logging.info('Package: %s, %s, %5.2f', \
                                package.city, package.accommodationType, 
                                package.basePriceInZAR)

        # now, carry on and look for availble accommodation
        venues = self.findVenues(element) 
        if venues:
            element.availableBerths = str(venues)
            berths = []
            for venue_key in venues:
                for key, slots in venues[venue_key]:
                    berth = Berth.get(key)
                    berths.append(berth)
            #Simply pull from the top of the list
            quote_amount = package.calculateQuote(element)
            people = element.adults + \
                     element.children 
            selected_berths = berths[:people]
            #sort
            selected_berths.sort(key=lambda b: "%s" % (
                    b.bed.bedroom.venue.fairAllocationsIndicator(
                      b, element)))
            self.createBookings(enquiry,
                              element,
                              [str(b.key()) for b in selected_berths])
            return (True, quote_amount)

        return (False, 0L)


    def findVenues(self, element):
        #Create an instance of a search  class and call it
        h1 = SimpleAccommodationSearch()
        return h1.findVenues(element)


    def createBookings(self, enquiry, element, selected_keys):
        #Mark slots as occupied
        error = None
        bookings = []
        try:
            people = 0
            init_enquiry_state = enquiry.workflowStateName
            #logger.info('AvailableBerths: %s', element.availableBerths)
            #logger.info('selected keys: %s', selected_keys)
            # Check if we have a package for the accommodation type in the city.
            query = Package.all()
            query.filter('city =', element.city)
            query.filter('accommodationType =', element.type)
            package = query.get()
            #get venues
            venues = eval(element.availableBerths)
            for venue_key in venues.keys():
                venue_affected = False
                for berth_key, slotkeys in venues[venue_key]:
                    #logger.info('test: %s', berth_key) 
                    if berth_key in selected_keys:
                        #Create Booking
                        booking = ContractedBooking(
                            parent=enquiry,
                            bookingNumber=generator.generateBookingNumber())
                        booking.put()
                        bookings.append(booking)
                        logger.info('Create booking: %s', booking.bookingNumber) 
                        people += 1
                        run_in_transaction(
                            self._assignBookingToSlots, 
                            enquiry, 
                            slotkeys, 
                            booking)
                        venue_affected = True
                if venue_affected:
                    Venue.get(venue_key).recalcNumOfBookings()

            if people:
                quote_amount = package.calculateQuote(element)
                enquiry.quoteInZAR = quote_amount
                enquiry.vatInZAR = long(quote_amount * 0.14)
                enquiry.totalAmountInZAR = enquiry.quoteInZAR + enquiry.vatInZAR
                if enquiry.workflowStateName == 'temporary':
                    enquiry.doTransition('allocatetemporary')
                elif enquiry.workflowStateName == 'awaitingagent':
                    enquiry.doTransition('allocatebyagent')
                else:
                    enquiry.doTransition('allocatefromhold')
                enquiry.put()

        except WorkflowError, error:
            logger.error('Workflow: %s', error) 
        except BookingConflictError, error:
            logger.error('BookingConflict: %s', error) 
        except:
            error = sys.exc_info()[1]
            logger.error('Other error; %s', error)

        if error:
            #Rollback and Clean up
            self.workflow = init_enquiry_state
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
        #Group slots by berth by venue in a dict
        #  {'v1': {'berth1':['slot1', 's2', 's3'],
        #          'berth2':['slot1', 's2', 's3']}}
        venues_dict = {}
        for slot in slots:
            #logger.info('Found berth %s', slot.berth.key())
            berth = slot.berth
            berth_key = str(berth.key())

            #venue = berth.bed.bedroom.venue
            #venue_key = str(venue.key())
            venue_key = slot.venue_key
            venue = Venue.get(venue_key)

            if venue.state == 'Closed':
                continue
            if not venues_dict.has_key(venue_key):
                venues_dict[venue_key] = {}
            berths_dict = venues_dict[venue_key]
            if berths_dict.has_key(berth_key):
                berths_dict[berth_key].append(str(slot.key()))
            else:
                berths_dict[berth_key] = [str(slot.key())]
        #logger.info('Found %s venues', venues_dict.keys()) 
        #Check for completeness - each berth has a slot for each night required
        valid_venues = {}
        for venue_key in venues_dict.keys():
            venue = venues_dict[venue_key]
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
        dates = getDateList(element.start, end)
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
        slots.filter('startDate in', dates)
        slots.order('startDate')
        logger.info('--------Found %s slots', len([s for s in slots]))
        #Run query and 
        return self._validateBerths(slots, element)



