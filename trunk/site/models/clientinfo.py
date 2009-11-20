from google.appengine.ext import db
from models.schedule import Match

from models.codelookup import getChoices

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
    state = db.StringProperty(default='Prospect', verbose_name='Status',
                        choices=getChoices('CLSTA'))
    dateOfBirth = db.DateProperty(verbose_name='Date of Birth')
    identityNumber = db.StringProperty(verbose_name='Identifying Number')
    identityNumberType = db.StringProperty(verbose_name='Identifying Number Type', 
                        choices=getChoices('IDTYP'))

    def listing_name(self):
        return '%s %s' % (self.firstNames, self.surname)

    def rdelete(self):
        for r in Flight.all().ancestor(self):
            r.rdelete()
        for r in MatchTicket.all().ancestor(self):
            r.rdelete()
        self.delete()

class Flight(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    number = db.StringProperty(
        required=True, verbose_name='Flight Number')
    airline = db.StringProperty(
        required=True, verbose_name='Airline')
    airport = db.StringProperty(
        required=True, verbose_name='Airport')
    direction = db.StringProperty(
        required=True, verbose_name='Direction',
        choices=getChoices('FLGTYP'))
    dateAtAirport = db.DateTimeProperty(verbose_name='Date/Time At Airport')

    def listing_name(self):
        return '%s' % self.flightNumber

    def rdelete(self):
        self.delete()

class MatchTicket(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    number = db.StringProperty(
        required=True, verbose_name='Ticket Number')
    match = db.StringProperty(required=True, 
        choices=['Game1', 'Game2'])
    #match = db.ReferenceProperty(Match,
    #    required=True, verbose_name='Match')

    def listing_name(self):
        return '%s' % self.flightNumber

    def rdelete(self):
        self.delete()

