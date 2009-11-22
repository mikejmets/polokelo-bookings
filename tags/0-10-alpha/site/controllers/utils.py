from google.appengine.api import users
def get_authentication_urls(dest_url):
    user = users.get_current_user()
    if user:
        return users.create_logout_url('/index'), 'Sign Out'
    else:
        return users.create_login_url(dest_url), 'Sign In'

from datetime import datetime,timedelta
def datetimeIterator(from_date=datetime.now(), to_date=None):
    while to_date is None or from_date <= to_date:
        yield from_date
        from_date = from_date + timedelta(days = 1)
    return

from models.hostinfo import *
def listVenuesValidity():
    results = ""
    total = 0
    valids = 0
    for owner in [o for o in Owner.all()]:
        venues = [v for v in Venue.all().ancestor(owner)]
        total += 1
        for venue in venues:
            is_valid = venue.isValid()
            if is_valid:
                valids += 1
            results += 'Owner %s %s: Venue %s: IsValid %s\n' % \
                (owner.surname,
                 owner.firstNames,
                 venue.name,
                 is_valid)

    return 'Valid/Total = %s/%s\n' % (valids, total) + results
    
def countAllEntities():
    results = ""
    results += countHostInfoEntities()
    results += "\n"
    results += countClientInfoEntities()
    results += "\n"
    results += countBookingInfoEntities()
    results += "\n"
    results += countOtherEntities()
    return results

def countHostInfoEntities():
    adict = {}
    adict['Owners'] = len([k for k in Owner.all(keys_only=True)])
    adict['Venues'] = len([k for k in Venue.all(keys_only=True)])
    adict['Bedroom'] = len([k for k in Bedroom.all(keys_only=True)])
    adict['Bed'] = len([k for k in Bed.all(keys_only=True)])
    adict['Berth'] = len([k for k in Berth.all(keys_only=True)])
    adict['Bathroom'] = len([k for k in Bathroom.all(keys_only=True)])
    adict['Photograph'] = len([k for k in Photograph.all(keys_only=True)])
    adict['Address'] = len([k for k in Address.all(keys_only=True)])
    adict['EmailAddress'] = len([k for k in EmailAddress.all(keys_only=True)])
    adict['PhoneNumber'] = len([k for k in PhoneNumber.all(keys_only=True)])
    adict['Inspection'] = len([k for k in Inspection.all(keys_only=True)])
    adict['Complaint'] = len([k for k in Complaint.all(keys_only=True)])
    adict['Slot'] = len([k for k in Slot.all(keys_only=True)])
    results = "Host Info\n"
    keys = adict.keys()
    keys.sort()
    for k in keys:
      results += "%s: %s\n" % (k, adict[k])
    return results

from models.clientinfo import *
def countClientInfoEntities():
    adict = {}
    adict['Client'] = len([k for k in Client.all(keys_only=True)])
    adict['Flight'] = len([k for k in Flight.all(keys_only=True)])
    adict['MatchTicket'] = len([k for k in MatchTicket.all(keys_only=True)])
    results = "Client Info\n"
    keys = adict.keys()
    keys.sort()
    for k in keys:
      results += "%s: %s\n" % (k, adict[k])
    return results

from models.bookinginfo import *
def countBookingInfoEntities():
    adict = {}
    adict['Enquiry'] = len([k for k in Enquiry.all(keys_only=True)])
    adict['AccommodationElement'] = \
        len([k for k in AccommodationElement.all(keys_only=True)])
    adict['GuestElement'] = len([k for k in GuestElement.all(keys_only=True)])
    adict['ContractedBooking'] = \
        len([k for k in ContractedBooking.all(keys_only=True)])
    results = "Booking Info\n"
    keys = adict.keys()
    keys.sort()
    for k in keys:
      results += "%s: %s\n" % (k, adict[k])
    return results

from models.schedule import *
from models.codelookup import *
def countOtherEntities():
    adict = {}
    adict['Match'] = len([k for k in Match.all(keys_only=True)])
    adict['CodeLookup'] = len([k for k in CodeLookup.all(keys_only=True)])
    results = "Other Info\n"
    keys = adict.keys()
    keys.sort()
    for k in keys:
      results += "%s: %s\n" % (k, adict[k])
    return results
