from google.appengine.ext import db


class Owner(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    referenceNumber = db.StringProperty(required=True)
    surname = db.StringProperty(required=True)
    firstNames = db.StringProperty(required=True)
    contactNumber = db.PhoneNumberProperty(required=True)
    emailAddress = db.EmailProperty(required=True)
    languages = db.StringListProperty()
    streetAddress = db.StringProperty(required=True)
    suburb = db.StringProperty(required=True)
    city = db.StringProperty()
    country = db.StringProperty(default='South Africa')
    postCode = db.StringProperty()
    addendumADate = db.DateProperty()
    addendumBDate = db.DateProperty()
    addendumCDate = db.DateProperty()
    trainingSession = db.DateProperty()

# class FinanceDetails
#     owner
#     registrationFeePaymentDate
#     bankName
#     branchCode
#     accountNumber
#     swiftCode
#     depositPaymentDate
#     finalPaymentDate
# 
# class Venue
#     owner
#     name
#     venueType
#     venueContactNumber
#     contactPerson
#     contactPersonNumber
#     streetAddress
#     suburb
#     city
#     country
#     postCode
#     keyPickupAddress
#     photo1
#     photo2
#     photo3
#     contractStartDate
#     contractEndDate
# 
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
