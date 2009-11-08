from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class Client(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    clientNumber = db.StringProperty(
        required=True, verbose_name='Guest Number')
    surname = db.StringProperty(
        required=True, verbose_name='Surname')
    firstNames = db.StringProperty(
        required=True, verbose_name='First Names')
    languages = db.StringListProperty(verbose_name='Languages')
    state = db.StringProperty(
        default="prospect", choices=["prospect", "confirmed"])
    dateOfBirth = db.DateProperty(verbose_name="Date of Birth")
    identityNumber = db.StringProperty(verbose_name="Identifying Number")
    identityNumberType = db.StringProperty(
        verbose_name="Identifying Number Type", 
        choices=["Passport", "IdentityDocument"])

    def listing_name(self):
        return "%s %s" % (self.firstNames, self.surname)

    def rdelete(self):
        self.delete()

