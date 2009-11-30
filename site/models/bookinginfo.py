from datetime import datetime
import logging
from google.appengine.ext import db

from models.clientinfo import Client
from models.codelookup import getChoices
from workflow.workflow import WorkflowAware

from controllers.emailtool import EmailTool

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
        for e in Enquiry.all().ancestor(self):
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

    def getContractedBookings(self):
        return ContractedBooking.all().ancestor(self).fetch(1000)

    def expire(self):
        for b in self.getContractedBookings():
            b.rdelete()

    def cancel(self):
        for b in self.getContractedBookings():
            b.rdelete()
    
    def allocate(self):
        element = AccommodationElement.all().ancestor(self)[0]
        et = EmailTool()
        et.notifyClientOfAllocation(self, element)

    def ontransition_expiretemporary(self, *args, **kw):
        pass

    def ontransition_expireallocated(self, *args, **kw):
        self.expire()

    def ontransition_expiredetails(self, *args, **kw):
        self.expire()

    def ontransition_expiredeposit(self, *args, **kw):
        self.expire()

    def ontransition_canceldeposit(self, *args, **kw):
        self.cancel()

    def ontransition_cancelfull(self, *args, **kw):
        self.cancel()

    def ontransition_allocate(self, *args, **kw):
        self.allocate()

    def ontransition_allocatemanually(self, *args, **kw):
        self.allocate()

    def ontransition_allocatefromhold(self, *args, **kw):
        self.allocate()

    def listing_name(self):
        return '%s' % self.referenceNumber

    def rdelete(self):
        for e in GuestElement.all().ancestor(self):
            e.rdelete()
        for e in AccommodationElement.all().ancestor(self):
            e.rdelete()
        for b in self.getContractedBookings():
            b.rdelete()
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
    availableBerths = db.TextProperty(default='{}')

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
    state = db.StringProperty(default='Temporary', 
            choices=getChoices('CBSTA'))

    def listing_name(self):
        return '%s' % (self.bookingNumber)

    def rdelete(self):
        venue = None
        for slot in self.slots:
            venue = slot.berth.bed.bedroom.venue
            slot.occupied = False
            slot.put()
        if venue:
            venue.recalcNumOfBookings()
        self.delete()


# payment tracking classes

class CollectionPaymentTracker(WorkflowAware):
    """ Track progress of payments for an enquiry collection
    """
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()


class EnquiryPaymentTracker(WorkflowAware):
    """ Track progress of payments for a specific enquiry
    """
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()


class VCSPaymentNotification(db.Model):
    """ Store VCS result data for the collection
    """
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    timeStamp = db.DateTimeProperty(verbose_name="Payment Time Stamp")

    terminalId = db.StringProperty(verbose_name="VCS Terminal ID")
    txRefNum = db.StringProperty(verbose_name="Unique Transaction Reference Number")
    txType = db.StringProperty("Transaction Type",
                            choices=("Authorisation", "Settlement", "Refund"))
    duplicateTransaction = db.BooleanProperty(verbose_name="Duplicate Transaction")
    authorised = db.BooleanProperty(default=False)
    authNumberOrReason = db.StringProperty( \
                            verbose_name="Approved Indicator or Rejection Reason")
    authResponseCode = db.StringProperty(verbose_name="Authorise Response Code")

    goodsDescription = db.StringProperty(verbose_name="Description of Goods Delivered")
    authAmount = db.FloatProperty(verbose_name="Amount Authorised")
    budgetPeriod = db.StringProperty(verbose_name="Budget Period")

    cardHolderName = db.StringProperty(verbose_name="Card Holder Name")
    cardHolderEmail = db.EmailProperty(verbose_name="Card Holder Email")
    cardHolderIP = db.StringProperty(verbose_name="Card Holder IP Address")

    maskedCardNumber = db.StringProperty("Masked Card Number")
    cardType = db.StringProperty(verbose_name="Card Type")
    cardExpiry = db.StringProperty(verbose_name="Card Expiry Date")

    pam = db.StringProperty(verbose_name="Personal Authentication Message")

    enquiryCollection = db.StringProperty(verbose_name="Enquiry Collection Number")
    enquiryList = db.StringListProperty(verbose_name="Enquiries affected by payment")
    paymentType = db.StringProperty(verbose_name="Payment Type", 
                            choices=("DEP", "INV"))
    depositPercentage = db.IntegerProperty(verbose_name="Deposit Percentage")
