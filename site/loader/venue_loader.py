import datetime
from google.appengine.ext import db
from google.appengine.tools import bulkloader
import models.hostinfo 
from google.appengine.api import users
import loader_utils

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
        ('addendumADate', 
          lambda x: str2datetimedate(x)),
        ('addendumBDate', 
          lambda x: str2datetimedate(x)),
        ('addendumCDate', 
          lambda x: str2datetimedate(x)),
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
                                ('addendumADate', str, None),
                                ('addendumBDate', str, None),
                                ('addendumCDate', str, None),
                                ('contractStartDate', str, None),
                                ('contractEndDate', str, None),
                               ])

exporters = [VenueExporter]
