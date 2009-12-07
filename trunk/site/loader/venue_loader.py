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
    bulkloader.Loader.__init__(self, 'Venue', [
        ('key', str),
        ('parent', str),
        ('created', lambda x: str2datetime(x)),
        ('creator', lambda x: users.User(x)),
        ('name', str),
        ('venueType', str),
        ('contactPerson', str),
        ('childFriendly', bool),
        ('contractStartDate', lambda x: str2datetimedate(x)),
        ('contractEndDate', lambda x: str2datetimedate(x)),
       ])

loaders = [VenueLoader]

def AddKeys(entity_generator):
    for entity in entity_generator:
        entity['key'] = entity.key()
        entity['parent'] = entity.parent()
        yield entity 

class VenueExporter(bulkloader.Exporter):
    def __init__(self):
      bulkloader.Exporter.__init__(self, 'Venue', [
            ('key', str, None),
            ('parent', str, None),
            ('created', str, None),
            ('creator', str, None),
            ('name', str, None),
            ('venueType', str, None),
            ('contactPerson', str, None),
            ('childFriendly', str, None),
            ('wheelchairAccess', str, False),
            ('specialNeeds', str, ''),
            ('registrationFeePaid', str, None),
            ('contractStartDate', str, None),
            ('contractEndDate', str, None),
           ])

    def output_entities(self, entity_generator):
        bulkloader.Exporter.output_entities(self, AddKeys(entity_generator)) 

exporters = [VenueExporter]
