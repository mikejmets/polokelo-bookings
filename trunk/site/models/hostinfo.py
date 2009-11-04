from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class Address(db.Model):
    container = db.ReferenceProperty(db.Model, collection_name='entity_addresses')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    addressType = db.StringProperty(required=True)
    streetAddress = db.StringProperty(required=True)
    suburb = db.StringProperty(required=True)
    city = db.StringProperty()
    country = db.StringProperty(default='South Africa')
    postCode = db.StringProperty()

    def listing_name(self):
        fields = [self.streetAddress, self.suburb, self.city, 
                  self.country, self.postCode]
        fields = [f for f in fields if (f.strip() != u'')]
        return "%s" % ", ".join(fields)

# class PhoneNumber

class Owner(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    referenceNumber = db.StringProperty(
        required=True, verbose_name='Reference Number')
    surname = db.StringProperty(required=True, verbose_name='Surname')
    firstNames = db.StringProperty(
        required=True, verbose_name='First Names')
    emailAddress = db.EmailProperty(
        required=True, verbose_name='Email Address')
    languages = db.StringListProperty(verbose_name='Languages')
    addendumADate = db.DateProperty(verbose_name='Addendum A Date')
    addendumBDate = db.DateProperty(verbose_name='Addendum B Date')
    addendumCDate = db.DateProperty(verbose_name='Addendum C Date')
    trainingSession = db.DateProperty(verbose_name='Training Session Date')

#class FinanceDetails(db.Model):
#    owner = db.ReferenceProperty(Owner)
#    registrationFeePaymentDate = db.DateProperty()
#    bankName = db.StringProperty()
#    branchCode = db.StringProperty()
#    accountNumber = db.StringProperty()
#    swiftCode = db.StringProperty()
#    depositPaymentDate = db.DateProperty()
#    finalPaymentDate = db.DateProperty()

class Venue(db.Model):
    owner = db.ReferenceProperty(Owner, collection_name='owner_venues')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    name = db.StringProperty(verbose_name='Venue Name')
    venueType = db.StringProperty(verbose_name='Class', 
                        choices=['Backpack', 'Hostel', 'Family House', 'Guest House'])
    contactPerson = db.StringProperty(verbose_name='Contact Person')
    contactPersonNumber = db.PhoneNumberProperty(verbose_name='Contact Person Number')
    keyPickupAddress = db.TextProperty(verbose_name='Where to pick up the key')
    photo1 = db.BlobProperty()
    photo2 = db.BlobProperty()
    photo3 = db.BlobProperty()
    contractStartDate = db.DateProperty(verbose_name='Contracted Start Date')
    contractEndDate = db.DateProperty(verbose_name='Contracted End Date')

# class Inspection
#     venue
#     date
#     notes
# 
# class Complaint
#     venue
#     date
#     notes
# 
# class Photo
#     thumbNail
#     fullSize
# 
# class Room
#     venue
#     bathroom
#     bathroomType
#     name
#     capacity
#     childrenUnder12
#     disabledFriendly
# 
# class Bathroom
#     venue
#     description
#     disabledFriendly
# 
# 
# class Bed
#     room
#     bedType
# 
# 
# class Berth
#     bed
# 
# 
# class Night
#     berth
#     booking
#     occupied
#     date
