import logging
from datetime import datetime, time

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.api import users

from models.codelookup import getChoices

from models.bookinginfo import ContractedBooking
from controllers.utils import datetimeIterator

logger = logging.getLogger('HostInfo')

class Address(db.Model):
    container = db.ReferenceProperty(db.Model, collection_name='entity_addresses')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    addressType = db.StringProperty(required=True, choices=getChoices('ADRTYP'))
    streetAddress = db.StringProperty(required=True)
    suburb = db.StringProperty(required=True)
    city = db.StringProperty(required=True, choices=getChoices('CTY'))
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
    numberType = db.StringProperty(verbose_name = 'Number Type',
                            required=True, choices=getChoices('NUMTP'))
    number = db.PhoneNumberProperty(verbose_name='Number', required=True)

    def rdelete(self):
        self.delete()


class EmailAddress(db.Model):
    container = db.ReferenceProperty(db.Model, collection_name='entity_emails')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    emailType = db.StringProperty(
            verbose_name = 'Email Type',
            required=True,
            choices=getChoices('EMLTP'))
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
    venueType = db.StringProperty(verbose_name='Class', 
        choices=getChoices('ACTYP'))
    contactPerson = db.StringProperty(verbose_name='Contact Person')
    disabilityFriendly = db.BooleanProperty(
        default=False, verbose_name='Disability Friendly')
    childFriendly = db.BooleanProperty(
        default=False, verbose_name='Child Friendly')
    registrationFeePaid = db.BooleanProperty(
        default=False, verbose_name='Registration Fee Paid')
    contractStartDate = db.DateProperty(verbose_name='Contracted Start Date')
    contractEndDate = db.DateProperty(verbose_name='Contracted End Date')
    state = db.StringProperty(default='Closed', choices=getChoices('VNSTA'))

    def get_city(self):
        q = Address.all()
        q.filter('addressType =', 'Physical')
        q.filter('container =', self)
        results = q.fetch(1)
        if results:
            return results[0].city

    def listing_name(self):
        return 'Name:%s Class:%s Contact:%s' % \
            (self.name, self.venueType, self.contactPerson)

    def create_slots(self):
        logging.info('Create slots for venue %s', self.name)
        for room in self.venue_bedrooms:
            for bed in room.bedroom_beds:
                for berth in bed.bed_berths:
                    logging.info('Create slot for berth %s', berth)
                    for slot in berth.berth_slots:
                        slot.delete()

                    for d in datetimeIterator(
                                  self.contractStartDate, 
                                  self.contractEndDate):
                        t = time(14, 00)
                        logging.info('Create slot for %s', 
                            datetime.combine(d, t))
                        slot = Slot()
                        slot.creator = users.get_current_user()
                        slot.berth = berth
                        slot.startDate = d #datetime.combine(d, t)
                        slot.city = berth.bed.bedroom.venue.get_city()
                        slot.type = berth.bed.bedroom.venue.venueType
                        slot.put()
                        
                        

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
    bathroomType = db.StringProperty(required=True, verbose_name='Bedroom Type',
                                        choices=getChoices('BRTYP'))
    disabilityFriendly = db.BooleanProperty(
        default=False, verbose_name='Disability Friendly')
    childFriendly = db.BooleanProperty(
        default=False, verbose_name='Child Friendly')
    capacity = db.IntegerProperty(
        required=True, default=1, verbose_name='Capacity')

    def listing_name(self):
        fields = [self.name, self.bathroomType, self.capacity]
        fields = [str(f) for f in fields]
        return '%s' % ', '.join(fields)

    def rdelete(self):
        for r in self.bedroom_beds:
            r.rdelete()
        self.delete()


class Bathroom(db.Model):
    venue = db.ReferenceProperty(Venue, collection_name='venue_bathrooms')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    description = db.TextProperty(required=True, verbose_name='Description')
    disabilityFriendly = db.BooleanProperty(
        default=False, verbose_name='Disability Friendly')

    def listing_name(self):
        return '%s' % self.description

    def rdelete(self):
        self.delete()

class Bed(db.Model):
    bedroom = db.ReferenceProperty(Bedroom, collection_name='bedroom_beds')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    name = db.StringProperty(required=True)
    bedType = db.StringProperty(required=True, choices=getChoices('BEDTP'))
    capacity = db.IntegerProperty(required=True, default=1)

    def listing_name(self):
        fields = [self.bedType, self.capacity]
        fields = [str(f) for f in fields]
        return '%s' % ', '.join(fields)

    def rdelete(self):
        for r in self.bed_berths:
            r.rdelete()
        self.delete()
        
class Berth(db.Model):
    bed = db.ReferenceProperty(Bed, collection_name='bed_berths')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()

    def rdelete(self):
        self.delete()
        
class Slot(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    berth = db.ReferenceProperty(Berth, collection_name='berth_slots')
    occupied = db.BooleanProperty(default=False)
    contracted_booking = db.ReferenceProperty(
        ContractedBooking, collection_name="slots")
    startDate = db.DateProperty()
    city = db.StringProperty()
    type = db.StringProperty()

    def listing_name(self):
        return 'Room:%s Venue:%s' % \
            (self.berth.bed.bedroom.name, self.berth.bed.bedroom.venue.name)

    def rdelete(self):
        self.delete()

