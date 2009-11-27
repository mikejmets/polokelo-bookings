from datetime import datetime
import logging
from google.appengine.ext import db

from models.clientinfo import Client
from models.codelookup import getChoices
from workflow.workflow import WorkflowAware

logger = logging.getLogger('BookingInfo')

class IdSequence(db.Model):
    """ keep track of sequences for number generators
    """
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    sequence = db.IntegerProperty(default=0)
    

class EnquiryCollection(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    referenceNumber = db.StringProperty(required=True, 
                                            verbose_name='Reference Number')

    def rdelete(self):
        for e in Enquiry.all.filter('ancestor =', self).fetch(1000):
            e.rdelete()
        self.delete()

class Enquiry(WorkflowAware):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    referenceNumber = db.StringProperty(verbose_name='Reference Number')
    expiryDate = db.DateTimeProperty(verbose_name="Expiry Date/Time (YYYY-MM-DD hh:mm)")
    guestEmail = db.StringProperty(verbose_name='Guest Email')
    agentCode = db.StringProperty(verbose_name='Travel Agent Code')
    quoteInZAR = db.FloatProperty(verbose_name='Quote', default=0.0)
    vatInZAR = db.FloatProperty(verbose_name='VAT', default=0.0)
    xmlSource = db.TextProperty(verbose_name='Source Detail')

    def ontransition_expiretemporary(self, *args, **kw):
        pass

    def ontransition_expireallocated(self, *args, **kw):
        for b in self.contracted_bookings:
            b.rdelete()

    def ontransition_expiredetails(self, *args, **kw):
        for b in self.contracted_bookings:
            b.rdelete()

    def ontransition_expiredeposit(self, *args, **kw):
        for b in self.contracted_bookings:
            b.rdelete()

    def ontransition_canceldeposit(self, *args, **kw):
        for b in self.contracted_bookings:
            b.rdelete()

    def ontransition_cancelfull(self, *args, **kw):
        for b in self.contracted_bookings:
            b.rdelete()

    def listing_name(self):
        return '%s' % self.referenceNumber

    def rdelete(self):
        for e in GuestElement.all().ancestor(self):
            e.rdelete()
        for e in AccommodationElement.all().ancestor(self):
            e.rdelete()
        self.delete()

class AccommodationElement(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    city = db.StringProperty(verbose_name='City',
        default='Potchefstroom', choices=getChoices('CTY'))
    type = db.StringProperty(default='Family Home', 
        verbose_name='Accommodation Class',
        choices=getChoices('ACTYP'))
    singlerooms = db.IntegerProperty(default=0)
    twinrooms = db.IntegerProperty(default=0)
    doublerooms = db.IntegerProperty(default=1)
    familyrooms = db.IntegerProperty(default=0)
    start = db.DateProperty(
        default=datetime(2010, 6, 1).date(),
        verbose_name='Start Date')
    nights = db.IntegerProperty(default=2)
    wheelchairAccess = db.BooleanProperty(default=False)
    specialNeeds = db.BooleanProperty(default=False)
    adults = db.IntegerProperty(default=2)
    children = db.IntegerProperty(default=0)
    xmlSource = db.TextProperty(verbose_name='Source Detail')
    availableBerths = db.TextProperty()

    def listing_name(self):
        return '%s' % self.city

    def rdelete(self):
        self.delete()

class GuestElement(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    enquiries = db.ListProperty(db.Key)
    isPrimary = db.BooleanProperty(default=False, verbose_name="Primary Guest")
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
    client = db.ReferenceProperty(
        Client, collection_name='contracted_bookings')
    enquiry = db.ReferenceProperty(
        Enquiry, collection_name='contracted_bookings')
    state = db.StringProperty(default='Temporary', 
            choices=getChoices('CBSTA'))

    def listing_name(self):
        return '%s' % self.bookingNumber

    def rdelete(self):
        for e in self.slots:
            e.occupied = False
            e.put()
        self.delete()

