import os
import logging
from datetime import datetime
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.utils import get_authentication_urls
from controllers.date_utils import parse_datetime
from models.bookinginfo import Enquiry
from models.hostinfo import Owner, Venue, Slot

logger = logging.getLogger("Tasks")

class ExpireEnquiries(webapp.RequestHandler):
    def get(self):
        logger.info("Expire Enquiries")
        enquiries = Enquiry.all()
        enquiries.filter('expiryDate !=', None)
        enquiries.filter('expiryDate <=', datetime.now())
        for enquiry in enquiries:
            transitions = enquiry.getPossibleTransitions()
            for t in transitions:
                if t.key().name().startswith('expire'):
                    logger.info("Expire enquiry -- %s", enquiry.referenceNumber)
                    enquiry.doTransition(t.key().name())
                    break

        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 'templates', 'index.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

class EmailGuests(webapp.RequestHandler):
    def get(self):
        logger.info("Email Guests")
        # Email guests/leads here
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 'templates', 'index.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))
class CreateSlotsTask(webapp.RequestHandler):
    def get(self):
        #loop through X venues on creation/mod date order
        #and create 50 slots if required
        #save venue to force date to change and thereby
        #influence the order
        logger.info("Create Slots Task")
        owners = Owner.all()
        owners.order('created')
        for owner in owners.fetch(1):
            logger.info("Create Slots for owner %s", owner.surname)
            venues = Venue.all()
            venues.filter('owner =', owner)
            venues.filter('state =', 'Open')
            venues.order('created')
            for venue in venues.fetch(1):
                logger.info('Create slots for venue %s %s', 
                    owner.surname, venue.name)
                venue.createSlots()
                venue.created = datetime.now()
                venue.put()
            owner.created = datetime.now()
            owner.put()
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 'templates', 'index.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

class CreateSlotsScript(webapp.RequestHandler):
    def get(self):
        venues = Venue.all().order('created')
        last_key = self.request.get('last_key', 'None')

        if last_key != 'None':
            last_key = parse_datetime(
                last_key, '%Y-%m-%d %H:%M:%S')
            venues.filter('created >', last_key)
            logger.info("Updating Datastore Script from %s", last_key)

        venues = venues.fetch(2)
        if len(venues) == 0:
            next_url = '/'
            last_key = '0'
        else:
            venues[0].createSlots()
            last_key = venues[1].created
            next_url = '/tasks/createslotsscript?last_key=%s' % str(last_key)

        context = {
                  'next_url': next_url,
                  }
        self.response.out.write(context) 

class UpdateDatastore(webapp.RequestHandler):
    def get(self):

        slots = Slot.all().order('created')
        last_key = self.request.get('last_key', 'None')
        current_key = '0' 

        if last_key != 'None':
            last_key = parse_datetime(
                last_key, '%Y-%m-%d %H:%M:%S')
            slots.filter('created >', last_key)
            current_key = last_key 
            logger.info("Updating Datastote Task from %s", last_key)


        slots = slots.fetch(5)
        if len(slots) == 0:
            next_url = '/'
            last_key = '0'
        else:
            for slot in slots:
                  slot.venue_capacity = \
                      slot.berth.bed.bedroom.venue.getCapacity()
                  slot.put()
            last_key = slots[-1].created
            next_url = '/tasks/update_datastore?last_key=%s' % str(last_key)

        context = {
                  'base_path':BASE_PATH,
                  'auth_url':auth_url,
                  'auth_url_text':auth_url_text,
                  'next_url': next_url,
                  }
        self.response.out.write(context) 


application = webapp.WSGIApplication([
      ('/tasks/expireenquiries', ExpireEnquiries),
      ('/tasks/emailguests', EmailGuests),
      ('/tasks/createslots', CreateSlotsTask),
      ('/tasks/createslotsscript', CreateSlotsScript),
      ('/tasks/update_datastore', UpdateDatastore),
      ], debug=False)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
