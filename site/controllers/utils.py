import re
from datetime import datetime,timedelta
from google.appengine.api import users
from models.hostinfo import Owner, Venue, Bedroom, Bed, Berth, Bathroom, \
    Photograph, Address, EmailAddress, PhoneNumber, Inspection, Complaint, \
    Slot
from models.clientinfo import Client, Flight, MatchTicket
from models.bookinginfo import EnquiryCollection, Enquiry, \
    AccommodationElement, GuestElement, ContractedBooking
from models.schedule import Match
from models.codelookup import CodeLookup

def get_authentication_urls(dest_url):
    user = users.get_current_user()
    if user:
        return users.create_logout_url('/index'), 'Sign Out'
    else:
        return users.create_login_url(dest_url), 'Sign In'

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

def countBookingInfoEntities():
    adict = {}
    adict['EnquiryCollection'] = len([k for k in Enquiry.all(keys_only=True)])
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


def parse_datetime(s, format):
    """Create datetime object representing date/time
    expressed in a string.

    This is required because converting microseconds using strptime() is only
    supported in Python 2.6.

    Takes a string in the format produced by calling str()
    on a python datetime or time objects and returns a datetime
    instance that would produce that string.

    Acceptable formats are: "YYYY-MM-DD HH:MM:SS.ssssss+HH:MM",
                            "YYYY-MM-DD HH:MM:SS.ssssss",
                            "YYYY-MM-DD HH:MM:SS+HH:MM",
                            "YYYY-MM-DD HH:MM:SS"
    Where ssssss represents fractional seconds.	 The timezone
    is optional and may be either positive or negative
    hours/minutes east of UTC.
    """
    if s is None:
        return None
    # Split string in the form 2007-06-18 19:39:25.3300-07:00
    # into its constituent date/time, microseconds, and
    # timezone fields where microseconds and timezone are
    # optional.
    m = re.match(r'(.*?)(?:\.(\d+))?(([-+]\d{1,2}):(\d{2}))?$',
                 str(s))
    datestr, fractional, tzname, tzhour, tzmin = m.groups()

    # Create tzinfo object representing the timezone
    # expressed in the input string.  The names we give
    # for the timezones are lame: they are just the offset
    # from UTC (as it appeared in the input string).  We
    # handle UTC specially since it is a very common case
    # and we know its name.
    if tzname is None:
        tz = None
    else:
        tzhour, tzmin = int(tzhour), int(tzmin)
        if tzhour == tzmin == 0:
            tzname = 'UTC'
        tz = FixedOffset(timedelta(hours=tzhour,
                                   minutes=tzmin), tzname)

    # Convert the date/time field into a python datetime
    # object.
    x = datetime.strptime(datestr, format)

    # Convert the fractional second portion into a count
    # of microseconds.
    if fractional is None:
        fractional = '0'
    fracpower = 6 - len(fractional)
    fractional = float(fractional) * (10 ** fracpower)

    # Return updated datetime object with microseconds and
    # timezone information.
    return x.replace(microsecond=int(fractional), tzinfo=tz)

