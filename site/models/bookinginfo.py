from google.appengine.ext import db
from models.clientinfo import Client
from models.hostinfo import Slot

class BookingRequest(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    referenceNumber = db.StringProperty(
        required=True, verbose_name='Reference Number')
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
    state = db.StringProperty(
        default='temporary', choices=['temporary', 'confirmed'])

    def listing_name(self):
        return '%s' % self.referenceNumber

    def rdelete(self):
        self.delete()

        
class ContractedBooking(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    bookingNumber = db.StringProperty(required=True)
    client = db.ReferenceProperty(
        Client, collection_name='client_contracted_bookings')
    slot = db.ReferenceProperty(
        Slot, collection_name='slot_contracted_bookings')
    request = db.ReferenceProperty(
        BookingRequest, collection_name='request_bookings')
    state = db.StringProperty(
        default='temporary', choices=['temporary', 'confirmed'])

    def listing_name(self):
        return '%s' % self.referenceNumber

    def rdelete(self):
        self.delete()

