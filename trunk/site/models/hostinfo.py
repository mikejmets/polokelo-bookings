from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class Address(db.Model):
    container = db.ReferenceProperty(
        db.Model, collection_name='entity_addresses')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    addressType = db.StringProperty(required=True,
        choices=['Physical', 'Postal', 'Key Collection', 'Other'])
    streetAddress = db.StringProperty(required=True)
    suburb = db.StringProperty(required=True)
    city = db.StringProperty()
    country = db.StringProperty(default='South Africa')
    postCode = db.StringProperty()

    def listing_name(self):
        fields = [self.streetAddress, self.suburb, self.city, 
                  self.country, self.postCode]
        fields = [f for f in fields if (f != None and f.strip() != u'')]
        return "%s" % ", ".join(fields)

class PhoneNumber(db.Model):
    container = db.ReferenceProperty(db.Model, collection_name='entity_phonenumbers')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    numberType = db.StringProperty(
            verbose_name = 'Number Type',
            required=True,
            choices=['Home', 'Work', 'Fax', 'Mobile'])
    number = db.PhoneNumberProperty(verbose_name='Number', required=True)


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

class Venue(db.Model):
    owner = db.ReferenceProperty(Owner, collection_name='owner_venues')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    name = db.StringProperty(verbose_name='Venue Name')
    venueType = db.StringProperty(verbose_name='Class', 
        choices=['Backpack', 'Hostel', 'Family House', 'Guest House'])
    contactPerson = db.StringProperty(verbose_name='Contact Person')
    photo1 = db.BlobProperty()
    photo2 = db.BlobProperty()
    photo3 = db.BlobProperty()
    disabilityFriendly = db.BooleanProperty(default=False)
    childFriendly = db.BooleanProperty(default=False)
    addendumADate = db.DateProperty(verbose_name='Addendum A Date')
    addendumBDate = db.DateProperty(verbose_name='Addendum B Date')
    addendumCDate = db.DateProperty(verbose_name='Addendum C Date')
    contractStartDate = db.DateProperty(verbose_name='Contracted Start Date')
    contractEndDate = db.DateProperty(verbose_name='Contracted End Date')

class Inspection(db.Model):
    venue = db.ReferenceProperty(Venue, collection_name='venue_inspections')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    inspectionDate = db.DateProperty(required=True)
    notes = db.TextProperty(required=True)

    def listing_name(self):
        fields = [self.inspectionDate, self.notes]
        fields = [str(f) for f in fields]
        return "%s" % ", ".join(fields)

class Complaint(db.Model):
    venue = db.ReferenceProperty(Venue, collection_name='venue_complaints')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    complaintDate = db.DateProperty(required=True)
    notes = db.TextProperty(required=True)

    def listing_name(self):
        fields = [self.complaintDate, self.notes]
        fields = [str(f) for f in fields]
        return "%s" % ", ".join(fields)

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
class BathRoom(db.Model):
    venue = db.ReferenceProperty(Venue, collection_name='venue_bathrooms')
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    description = db.TextProperty(required=True)
    disabilityFriendly = db.BooleanProperty(required=True, default=False)

    def listing_name(self):
        fields = [self.description, self.disabledFriendly]
        fields = [str(f) for f in fields]
        return "%s" % ", ".join(fields)

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
