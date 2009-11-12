from google.appengine.ext import db
from models.clientinfo import Client
from models.hostinfo import Slot

class Enquiry(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    referenceNumber = db.StringProperty(
        required=True, verbose_name='Reference Number')
    state = db.StringProperty(
        default='temporary', choices=['temporary', 'confirmed'])
    xmlSource = db.TextProperty(verbose_name='Source Detail')

    def listing_name(self):
        return '%s' % self.referenceNumber

    def rdelete(self):
        self.delete()

class AccommodationElement(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    enquiry = db.ReferenceProperty(
        Enquiry, collection_name='accommodation_elements')
    city = db.StringProperty(
        required=True, 
        verbose_name='City',
        default='Potchefstroom',
        choices=['Potchefstroom', 'Cape Town'])
    serviceType = db.StringProperty(
        required=True, 
        verbose_name='Accommodation Class',
        choices=['Backpackers', 'Guest House', 'Home Stay', 'Hostel'])
    startDate = db.DateProperty(
        required=True, verbose_name='Start Date')
    duration = db.IntegerProperty(
        required=True, verbose_name='Number of nights')
    quantity = db.IntegerProperty(
        required=True, verbose_name='Number of people')
    xmlSource = db.TextProperty(verbose_name='Source Detail')

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
        
class ContractedBooking(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    bookingNumber = db.StringProperty(required=True)
    client = db.ReferenceProperty(
        Client, collection_name='contraced_bookings')
    slot = db.ReferenceProperty(
        Slot, collection_name='contracted_bookings')
    enquiry = db.ReferenceProperty(
        Enquiry, collection_name='contracted_bookings')
    state = db.StringProperty(
        default='temporary', choices=['temporary', 'confirmed'])

    def listing_name(self):
        return '%s' % self.bookingNumber

    def rdelete(self):
        self.delete()

