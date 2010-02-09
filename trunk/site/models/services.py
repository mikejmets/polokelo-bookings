import logging
from google.appengine.ext import db
from models.hostinfo import Address

logger = logging.getLogger('Services')

class ServiceProvider(db.Model):
    """ Organisations that offer services
    """
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    name = db.StringProperty(
        required=True, verbose_name='Name')

    def rdelete(self):
        self.delete()

class Service(db.Model):
    """ All services on which bookings can be made
    """
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    name = db.StringProperty(
        required=True, verbose_name='Name')
    description = db.TextProperty(
        required=True, verbose_name='Description')

    def rdelete(self):
        self.delete()


