from google.appengine.ext import db
from google.appengine.ext.db import polymodel

#class Contact(db.Model):
#    contactNumber = db.PhoneNumberProperty(required=True)
#    streetAddress = db.StringProperty(required=True)
#    suburb = db.StringProperty(required=True)
#    city = db.StringProperty()
#    country = db.StringProperty(default='South Africa')
#    postCode = db.StringProperty()

class Owner(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    referenceNumber = db.StringProperty(
        required=True, verbose_name='Reference Number')
    surname = db.StringProperty(required=True)
    firstNames = db.StringProperty(
        required=True, verbose_name='First Name')
    emailAddress = db.EmailProperty(
        required=True, verbose_name='Email Address')
    languages = db.StringListProperty()
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
    owner = db.ReferenceProperty(Owner)
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    name = db.StringProperty()
    venueType = db.StringListProperty()
    contactPerson = db.StringProperty()
    contactPersonNumber = db.PhoneNumberProperty()
    keyPickupAddress = db.StringProperty()
    photo1 = db.BlobProperty()
    photo2 = db.BlobProperty()
    photo3 = db.BlobProperty()
    contractStartDate = db.DateProperty()
    contractEndDate = db.DateProperty()

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
