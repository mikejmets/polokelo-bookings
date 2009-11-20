from datetime import datetime
from google.appengine.ext import db
from models.clientinfo import Client

from models.codelookup import getChoices

class Enquiry(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    referenceNumber = db.StringProperty(
        required=True, verbose_name='Reference Number')
    state = db.StringProperty(default='Temporary', choices=getChoices('EQSTA'))
    xmlSource = db.TextProperty(verbose_name='Source Detail')

    def listing_name(self):
        return '%s' % self.referenceNumber

    def rdelete(self):
        for e in self.guest_elements:
            e.rdelete()
        for e in self.accommodation_elements:
            e.rdelete()
        self.delete()

class AccommodationElement(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    enquiry = db.ReferenceProperty(
        Enquiry, collection_name='accommodation_elements')
    city = db.StringProperty(verbose_name='City',
        default='Potchefstroom', choices=getChoices('CTY'))
    type = db.StringProperty(default='Family Home', 
        verbose_name='Accommodation Class',
        choices=getChoices('ACTYP'))
    start = db.DateProperty(
        default=datetime(2010, 6, 1),
        verbose_name='Start Date')
    nights = db.IntegerProperty(default=0)
    wheelchairAccess = db.BooleanProperty(default=False)
    specialNeeds = db.BooleanProperty(default=False)
    genderSensitive = db.BooleanProperty(default=False)
    adultMales = db.IntegerProperty(default=0)
    adultFemales = db.IntegerProperty(default=0)
    childMales = db.IntegerProperty(default=0)
    childFemales = db.IntegerProperty(default=0)
    xmlSource = db.TextProperty(verbose_name='Source Detail')
    availableBerths = db.TextProperty()

    def listing_name(self):
        return '%s' % self.city

    def rdelete(self):
        self.delete()

class GuestElement(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    enquiry = db.ReferenceProperty(
        Enquiry, collection_name='guest_elements')
    isPrimary = db.BooleanProperty(default=True, verbose_name="Primary Guest")
    surname = db.StringProperty(required=True)
    firstNames = db.StringProperty(required=True, verbose_name="First Names")
    email = db.EmailProperty(verbose_name='Email Address')
    contactNumber = db.PhoneNumberProperty(verbose_name='Contact Number')
    identifyingNumber = db.StringProperty(verbose_name='Identifying Number')
    xmlSource = db.TextProperty(verbose_name='Source Detail')
        
    def rdelete(self):
        self.delete()

class ContractedBooking(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    bookingNumber = db.StringProperty(required=True)
    duration = db.IntegerProperty()
    client = db.ReferenceProperty(
        Client, collection_name='contracted_bookings')
    enquiry = db.ReferenceProperty(
        Enquiry, collection_name='enquiries')
    state = db.StringProperty(default='Temporary', 
            choices=getChoices('CBSTA'))

    def listing_name(self):
        return '%s' % self.bookingNumber

    def rdelete(self):
        for e in self.slots:
            e.occupied = False
            e.put()
        self.delete()

