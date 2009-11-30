import datetime
from google.appengine.ext import db
from google.appengine.tools import bulkloader
from models.hostinfo import Owner
from google.appengine.api import users
import loader.loader_utils

def findContainer(x):
  return Owner.get(x)

class PhoneNumberLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'PhoneNumber',
       [
        ('container', lambda x: findContainer(x)),
        ('created', 
          lambda x: str2datetime(x)),
        ('creator', 
          lambda x: users.User(x)),
        ('numberType', str),
        ('number', str),
       ])

loaders = [PhoneNumberLoader]

class PhoneNumberExporter(bulkloader.Exporter):
  def __init__(self):
    bulkloader.Exporter.__init__(self, 'PhoneNumber',
       [
        ('container', str, None),
        ('created', str, None),
        ('creator', str, None),
        ('numberType', str, None),
        ('number', str, None),
       ])

exporters = [PhoneNumberExporter]
