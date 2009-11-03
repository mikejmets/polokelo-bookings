import datetime
from google.appengine.ext import db
from google.appengine.tools import bulkloader
import models.hostinfo 
from google.appengine.api import users

class OwnerLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'Owner',
       [('created', 
          lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')),
        ('creator', 
          lambda x: users.User(x)),
        ('referenceNumber', str),
        ('surname', str),
        ('firstNames', str),
        ('contactNumber', str),
        ('emailAddress', str),
        ('languages', eval),
        ('streetAddress', str),
        ('suburb', str),
        ('city', str),
        ('country', str),
        ('postCode', str),
        ('addendumADate', 
          lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date()),
        ('addendumBDate', 
          lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date()),
        ('addendumCDate', 
          lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date()),
        ('trainingSession', 
          lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date()),
       ])

loaders = [OwnerLoader]

class OwnerExporter(bulkloader.Exporter):
  def __init__(self):
    bulkloader.Exporter.__init__(self, 'Owner',
                               [('created', str, None),
                                ('creator', str, None),
                                ('referenceNumber', str, None),
                                ('surname', str, None),
                                ('firstNames', str, None),
                                ('contactNumber', str, None),
                                ('emailAddress', str, None),
                                ('languages', list, None),
                                ('streetAddress', str, None),
                                ('suburb', str, None),
                                ('city', str, None),
                                ('country', str, None),
                                ('postCode', str, None),
                                ('addendumADate', str, None),
                                ('addendumBDate', str, None),
                                ('addendumCDate', str, None),
                                ('trainingSession', str, None),
                               ])

exporters = [OwnerExporter]
