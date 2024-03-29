import logging
from datetime import datetime, time, timedelta

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.api import users

from models.bookinginfo import ContractedBooking
from controllers.date_utils import getDateList

def datetimeIterator(from_date=datetime.now(), to_date=None):
    while to_date is None or from_date <= to_date:
        yield from_date
        from_date = from_date + timedelta(days = 1)
    return


logger = logging.getLogger('HostInfo')

class Address(db.Model):
    container = db.ReferenceProperty(db.Model, collection_name='entity_addresses')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    addressType = db.StringProperty(required=True)
    streetAddress = db.StringProperty(required=True)
    suburb = db.StringProperty()
    city = db.StringProperty(required=True)
    country = db.StringProperty(default='South Africa')
    postCode = db.StringProperty()

    def listing_name(self):
        fields = [self.streetAddress, self.suburb, self.city, 
                  self.country, self.postCode]
        fields = [f for f in fields if (f != None and f.strip() != u'')]
        return '%s' % ', '.join(fields)

    def rdelete(self):
        self.delete()


class PhoneNumber(db.Model):
    container = db.ReferenceProperty(db.Model, collection_name='entity_phonenumbers')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    numberType = db.StringProperty(verbose_name = 'Number Type', required=True)
    number = db.PhoneNumberProperty(verbose_name='Number', required=True)
    def rdelete(self):
        self.delete()


class EmailAddress(db.Model):
    container = db.ReferenceProperty(db.Model, collection_name='entity_emails')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    emailType = db.StringProperty(verbose_name = 'Email Type', required=True)
    email = db.EmailProperty(verbose_name='Email Address', required=True)

    def rdelete(self):
        self.delete()


class Owner(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    referenceNumber = db.StringProperty(
        required=True, verbose_name='Reference Number')
    surname = db.StringProperty(required=True, verbose_name='Surname')
    firstNames = db.StringProperty(
        required=True, verbose_name='First Names')
    languages = db.StringListProperty(verbose_name='Languages')

    def listing_name(self):
        return '%s %s' % (self.firstNames, self.surname)

    def rdelete(self):
        for r in self.owner_venues:
            r.rdelete()
        for r in self.entity_addresses:
            r.rdelete()
        for r in self.entity_emails:
            r.rdelete()
        for r in self.entity_phonenumbers:
            r.rdelete()
        self.delete()


class Venue(db.Model):
    owner = db.ReferenceProperty(Owner, collection_name='owner_venues')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    name = db.StringProperty(verbose_name='Venue Name')
    venueType = db.StringProperty(verbose_name='Class') 
    contactPerson = db.StringProperty(verbose_name='Contact Person')
    childFriendly = db.BooleanProperty(
        default=True, verbose_name='Child Friendly')
    wheelchairAccess = db.BooleanProperty(
        default=False, verbose_name='Wheelchair Access')
    specialNeeds = db.StringProperty(verbose_name='Special Needs')
    registrationFeePaid = db.BooleanProperty(
        default=False, verbose_name='Registration Fee Paid')
    contractStartDate = db.DateProperty(verbose_name='Contracted Start Date (YYYY-MM-DD)')
    contractEndDate = db.DateProperty(verbose_name='Contracted End Date (YYYY-MM-DD)')
    state = db.StringProperty(default='Closed')
    numberOfBookings = db.IntegerProperty(default=0)

    def get_city(self):
        results = Address.all()
        results.filter('addressType =', 'Physical Address')
        results.filter('container =', self)
        address = results.fetch(1)
        if address:
            return address[0].city

    def listing_name(self):
        return 'Name:%s Class:%s Contact:%s' % \
            (self.name, self.venueType, self.contactPerson)

    def fairAllocationsIndicator(self, berth, element):
        #Create a string for fairness sorting

        #Keep allocations within single digits
        #For home and guest house, ensure unallocated venues are higher
        allocations = min(self.numberOfBookings, 9)
        if self.venueType in ['Hostel', 'Back Packers']:
            #fill up one hostel completely first
            allocations = 9 - allocations

        #If double rooms required, ensure bouble room are higher
        doubles = element.doublerooms
        if doubles > 0:
            double_indicator = 9
            if berth.bed.bedType == 'Double':
                doubles = min(doubles, 9)
                double_indicator = 9 - doubles
        else:
            double_indicator = 0
            if berth.bed.bedType == 'Double':
                double_indicator = 9
        return "%s %s %s %s %s %s" % (
            allocations, 
            double_indicator, 
            self.owner.referenceNumber,
            self.name,
            berth.bed.bedroom.name,
            berth.bed.name)

    def hasBookings(self):
        return self.numberOfBookings > 0

    def recalcNumOfBookings(self):
        self.numberOfBookings = len(self.getContractedBookings())
        #logger.info('Recalc venue %s to %d', self.name, self.numberOfBookings)
        self.put()

    def getContractedBookings(self):
        bookings = set()
        for room in self.venue_bedrooms:
            bookings.update(room.getContractedBookings())
        return bookings

    def isValid(self):
        is_valid, err = self.validate()
        #if not is_valid:
        #    logger.info("Validation failed: %s", err)
        return is_valid

    def canModify(self):
        return self.state != 'Open'

    def validate(self, skip_rooms=False):
        #Check venue fields
        if not self.registrationFeePaid:
            return False, "Registration fee not received"
        if not (self.contractStartDate and self.contractEndDate):
            return False, "Missing contract dates"

        if not skip_rooms:
            #Check bedrooms
            for b in self.venue_bedrooms:
                is_valid, err = b.validate()
                if not is_valid:
                    return False, err

        #Check bathrooms
        if len(self.venue_bathrooms.fetch(1)) == 0:
            return False, "No bathrooms in venue"
        
        #Check physical address exists
        has_address = False
        for a in Address.all().ancestor(self):
            if a.addressType == 'Physical Address':
                has_address = True
                break
        #if not has_address:
        #    for a in Address.all().ancestor(self.parent()): 
        #        if a.addressType == 'Physical Address':
        #            has_address = True
        #            break
        if not has_address:
            return False, "No physical address for venue"

        #Ensure contact
        #has_email = len(self.entity_emails.fetch(1)) > 0
        #has_number = len(self.entity_phonenumbers.fetch(1)) > 0
        #if not has_email and not has_number:
        #    return False, "No contactable"

        #Check photos
        #if len(self.venue_photos.fetch(1)) == 0:
        #    return False, "No Photos"

        #Recalc numberOfBookings
        if self.numberOfBookings > 0:
            self.recalcNumOfBookings()

 
        #Otherwise
        return True, ""

    def createSlots(self, limit=10):
        #logging.info('Create slots for venue %s', self.name)
        counter = 0
        for room in self.venue_bedrooms:
            for bed in room.bedroom_beds:
                for berth in bed.bed_berths:
                    slots = berth.createSlots(self, room, bed, limit)
                    counter += slots
                    if limit and counter >= limit:
                        #Jump out so that the request doesn't timeout
                        return counter
        return counter

    def validateSlots(self):
        #logging.info('Create slots for venue %s', self.name)
        numNights = 0
        numSlots = 0
        for room in self.venue_bedrooms:
            for bed in room.bedroom_beds:
                for berth in bed.bed_berths:
                    td = self.contractEndDate - self.contractStartDate
                    numNights += td.days + 1
                    numSlots += len(
                        [s for s in Slot.all(keys_only=True).ancestor(berth)])
        return numNights, numSlots
                        
    def deleteAllSlots(self):
        #Beware: this may leave bookings hanging
        for room in self.venue_bedrooms:
            for bed in room.bedroom_beds:
                for berth in bed.bed_berths:
                    for slot in berth.berth_slots:
                        slot.rdelete()


    def deleteSlots(self, limit=10):
        counter = 0
        for room in self.venue_bedrooms:
            for bed in room.bedroom_beds:
                for berth in bed.bed_berths:
                    for slot in berth.berth_slots:
                        counter += 1
                        slot.rdelete()
                        if limit and counter >= limit:
                            #Jump out so that the request doesn't timeout
                            return counter
        return counter
    def getCapacity(self):
        cap = 0
        for b in self.venue_bedrooms:
            cap += b.capacity
        return cap

    def rdelete(self):
        for r in self.venue_inspections:
            r.rdelete()
        for r in self.venue_complaints:
            r.rdelete()
        for r in self.venue_bedrooms:
            r.rdelete()
        for r in self.venue_bathrooms:
            r.rdelete()
        for r in self.entity_addresses:
            r.rdelete()
        for r in self.entity_emails:
            r.rdelete()
        for r in self.entity_phonenumbers:
            r.rdelete()
        for r in self.venue_photos:
            r.rdelete()
        self.delete()

class Photograph(db.Model):
    venue = db.ReferenceProperty(Venue, collection_name='venue_photos')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    caption = db.StringProperty()
    thumbnail = db.BlobProperty()
    fullsize = db.BlobProperty()

    def rdelete(self):
        self.delete()

class Inspection(db.Model):
    venue = db.ReferenceProperty(Venue, collection_name='venue_inspections')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    inspectionDate = db.DateProperty(required=True)
    notes = db.TextProperty(required=True)

    def listing_name(self):
        fields = [self.inspectionDate, self.notes]
        fields = [str(f) for f in fields]
        return '%s' % ', '.join(fields)

    def rdelete(self):
        self.delete()


class Complaint(db.Model):
    venue = db.ReferenceProperty(Venue, collection_name='venue_complaints')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    complaintDate = db.DateProperty(required=True)
    notes = db.TextProperty(required=True)

    def listing_name(self):
        fields = [self.complaintDate, self.notes]
        fields = [str(f) for f in fields]
        return '%s' % ', '.join(fields)

    def rdelete(self):
        self.delete()

class Bedroom(db.Model):
    venue = db.ReferenceProperty(Venue, collection_name='venue_bedrooms')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    name = db.StringProperty(required=True, verbose_name='Name')
    bedroomType = db.StringProperty( verbose_name='Bedroom Type')
    bathroomType = db.StringProperty(
        required=True, verbose_name='Bathroom Type')
    childFriendly = db.BooleanProperty(
        default=True, verbose_name='Child Friendly')
    wheelchairAccess = db.BooleanProperty(
        default=False, verbose_name='Wheelchair Access')
    specialNeeds = db.StringProperty(verbose_name='Special Needs')
    capacity = db.IntegerProperty(
        required=True, default=1, verbose_name='Capacity')

    def listing_name(self):
        fields = [self.name, self.bathroomType, self.capacity]
        fields = [str(f) for f in fields]
        return '%s' % ', '.join(fields)

    def validate(self):
        #Check beds exist
        if len(self.bedroom_beds.fetch(1)) == 0:
            return False, "No Beds in bedroom %s" % self.name

        #Check bedroom capacity > 0
        if self.capacity == 0:
            return False, "No capacity in bedroom %s" % self.name

        #Check type is captured
        if not self.bedroomType:
            return False, "Type not specified in bedroom %s" % self.name

        #Check capacity matches
        bed_cap = 0
        for b in self.bedroom_beds:
            bed_cap += b.capacity
        if bed_cap != self.capacity:
            return False, "Capacity mismatch in bedroom %s" % self.name

        return True, ""

    def rdelete(self):
        for r in self.bedroom_beds:
            r.rdelete()
        self.delete()

    def getContractedBookings(self):
        bookings = set()
        for bed in self.bedroom_beds:
            bookings.update(bed.getContractedBookings())
        return bookings

class Bathroom(db.Model):
    venue = db.ReferenceProperty(Venue, collection_name='venue_bathrooms')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    description = db.TextProperty(required=True, verbose_name='Description')
    wheelchairAccess = db.BooleanProperty(
        default=False, verbose_name='Wheelchair Access')

    def listing_name(self):
        return '%s' % self.description

    def rdelete(self):
        self.delete()

class Bed(db.Model):
    bedroom = db.ReferenceProperty(Bedroom, collection_name='bedroom_beds')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    name = db.StringProperty()
    bedType = db.StringProperty(required=True)
    capacity = db.IntegerProperty(required=True, default=1)

    def listing_name(self):
        fields = [self.bedType, self.capacity]
        fields = [str(f) for f in fields]
        return '%s' % ', '.join(fields)

    def isValid(self):
        return self.capacity == len([b for b in self.bed_berths])
        
    def rdelete(self):
        for r in self.bed_berths:
            r.rdelete()
        self.delete()
        
    def getContractedBookings(self):
        bookings = set()
        for berth in self.bed_berths:
            bookings.update(berth.getContractedBookings())
        return bookings

    def createBerths(self):
        for i in range(self.capacity):
            berth = Berth(parent=self)
            berth.creator = users.get_current_user()
            berth.bed = self
            berth.put()
            #logger.info('Created berth %s', i)

class Berth(db.Model):
    bed = db.ReferenceProperty(Bed, collection_name='bed_berths')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()

    def rdelete(self):
        for r in self.berth_slots:
            r.rdelete()
        self.delete()

    def getContractedBookings(self):
        bookings = set()
        for slot in self.berth_slots:
            if hasattr(slot, 'contracted_booking') and \
               slot.contracted_booking:
                bookings.add(str(slot.contracted_booking.key()))
        return bookings

    def createSlots(self, venue=None, room=None, bed=None, limit=10):
        cnt = 0
        if bed is None:
            bed = self.bed
        if room is None:
            room = bed.bedroom
        if venue is None:
            venue = room.venue

        start_date = max(datetime.now().date(), venue.contractStartDate) 

        all_dates = getDateList(start_date, venue.contractEndDate)
        slot_dates = \
            [s.startDate for s in Slot.all().ancestor(self)]
        new_dates = [d for d in all_dates if d not in slot_dates]

        #logger.info('-----------Slot date %s', new_dates)
        for d in new_dates:
            t = time(14, 00)
            slots = Slot.all().ancestor(self)
            slots.filter('startDate =', d)
            if slots.get():
                continue
            logger.debug('-----------Create slot for %s', d)
            slot = Slot(parent=self)
            slot.creator = users.get_current_user()
            slot.ownerReference = venue.owner.referenceNumber
            slot.berth = self
            slot.startDate = d #datetime.combine(d, t)
            slot.city = venue.get_city()
            slot.venueType = venue.venueType
            slot.bedType = bed.bedType
            slot.childFriendly = \
                venue.childFriendly or \
                room.childFriendly 
            slot.wheelchairAccess = \
                venue.wheelchairAccess or \
                room.wheelchairAccess 
            slot.venue_key = str(venue.key())
            slot.venue_capacity = venue.getCapacity()
            slot.put()
            cnt += 1
            if limit and cnt > limit:
                #jump out early
                return cnt
        return cnt

class Slot(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    ownerReference = db.StringProperty()
    berth = db.ReferenceProperty(Berth, collection_name='berth_slots')
    occupied = db.BooleanProperty(default=False)
    contracted_booking = db.ReferenceProperty(
        ContractedBooking, collection_name="slots")
    startDate = db.DateProperty()
    city = db.StringProperty()
    venueType = db.StringProperty()
    bedType = db.StringProperty()
    childFriendly = db.BooleanProperty()
    wheelchairAccess = db.BooleanProperty()
    venue_key = db.StringProperty()
    venue_capacity = db.IntegerProperty(default=0)

    def listing_name(self):
        return 'Room:%s Venue:%s' % \
            (self.berth.bed.bedroom.name, self.berth.bed.bedroom.venue.name)

    def rdelete(self):
        self.delete()

