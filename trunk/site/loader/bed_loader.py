import datetime
import logging
logger = logging.getLogger('owner_loader')

from google.appengine.ext import db
from google.appengine.tools import bulkloader
from google.appengine.api import datastore
from google.appengine.api import users

from models.hostinfo import Bed 

def str2datetime(x):
    if x != 'None':
        x = x.split(".")[0]
        x = datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
    return x

def noneStr(x):
    if x == 'None':
        x = None
    return x

def getUser(x):
    return users.User(x)

class BedLoader(bulkloader.Loader):
    def __init__(self):
        bulkloader.Loader.__init__(self, 'Bed', [
            ('key', str),
            ('parent', noneStr),
            ('created', str2datetime),
            ('creator', users.User),
            ('referenceNumber', str),
            ('surname', str),
            ('firstNames', str),
            ('languages', eval),
           ])

    def generate_key(self, i, values):
        key = datastore.Key(values[0])
        logger.info('GenKey===========%s %s %s', key, key.name(), isinstance(key.id(), long))
        return key

    def handle_entity(self, entity):
        logger.info('Handle===========%s', entity.key().__dict__)
        return entity


loaders = [BedLoader]

"""
Exporting
"""
def AddKeys(entity_generator):
    for entity in entity_generator:
        entity['key'] = entity.key()
        entity['parent'] = entity.parent()
        yield entity 

class BedExporter(bulkloader.Exporter):
    def __init__(self):
      bulkloader.Exporter.__init__(self, 'Bed', [
          ('key', str, None),
          ('parent', str, None),
          ('bedroom', str, None),
          ('created', str, None),
          ('creator', str, None),
          ('name', str, ''),
          ('bedType', str, 'Single'),
          ('capacity', str, None),
         ])

    def output_entities(self, entity_generator):
        bulkloader.Exporter.output_entities(self, AddKeys(entity_generator)) 

exporters = [BedExporter]
