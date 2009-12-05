import datetime
import logging
logger = logging.getLogger('owner_loader')


from google.appengine.ext import db
from google.appengine.tools import bulkloader
from google.appengine.api import users

from models.hostinfo import Owner 

#DOESN"T FCKING WORK from loader_utils import str2datetime
def str2datetime(x):
  if x != 'None':
      x = x.split(".")[0]
      x = datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
  return x


class OwnerLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'Owner', [
        ('created', 
          lambda x: str2datetime(x)),
        ('creator', 
          lambda x: users.User(x)),
        ('referenceNumber', str),
        ('surname', str),
        ('firstNames', str),
        ('languages', eval),
       ])

loaders = [OwnerLoader]

class OwnerExporter(bulkloader.Exporter):
  def __init__(self):
    bulkloader.Exporter.__init__(self, 'Owner', [
        ('key', lambda k:k.__call__(), None),
        ('created', str, None),
        ('creator', str, None),
        ('referenceNumber', str, None),
        ('surname', str, None),
        ('firstNames', str, None),
        ('languages', list, None),
       ])

exporters = [OwnerExporter]
