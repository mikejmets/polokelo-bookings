import datetime
import logging

logger = logging.getLogger('venue_loader')

from google.appengine.ext import db
from google.appengine.tools import bulkloader
from google.appengine.api import users

from models.hostinfo import Venue
from loader_utils import str2datetime, str2datetimedate

class VenueLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'Venue',
       [('created', 
          lambda x: str2datetime(x)),
        ('creator', 
          lambda x: users.User(x)),
        ('name', str),
        ('venueType', str),
        ('contactPerson', str),
        ('disabilityFriendly', bool),
        ('childFriendly', bool),
        ('contractStartDate', 
          lambda x: str2datetimedate(x)),
        ('contractEndDate', 
          lambda x: str2datetimedate(x)),
       ])

loaders = [VenueLoader]

class VenueExporter(bulkloader.Exporter):
  def __init__(self):
    bulkloader.Exporter.__init__(self, 'Venue',
                               [('created', str, None),
                                ('creator', str, None),
                                ('name', str, None),
                                ('venueType', str, None),
                                ('contactPerson', str, None),
                                ('disabilityFriendly', str, None),
                                ('childFriendly', str, None),
                                ('contractStartDate', str, None),
                                ('contractEndDate', str, None),
                               ])

exporters = [VenueExporter]
