import re
from datetime import datetime,timedelta
from google.appengine.api import users

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

def getDateList(from_date, to_date):
    dates = []
    if to_date < from_date:
        return dates

    while from_date <= to_date:
        dates.append(from_date)
        from_date = from_date + timedelta(days = 1)

    return dates

