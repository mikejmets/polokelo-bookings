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
    referenceNumber = db.StringProperty(required=True)
    surname = db.StringProperty(required=True)
    firstNames = db.StringProperty(required=True)
    emailAddress = db.EmailProperty(required=True)
    languages = db.StringListProperty()
    addendumADate = db.DateProperty()
    addendumBDate = db.DateProperty()
    addendumCDate = db.DateProperty()
    trainingSession = db.DateProperty()

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
