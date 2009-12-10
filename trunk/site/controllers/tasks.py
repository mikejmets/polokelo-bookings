import os
import logging
from datetime import datetime
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.utils import get_authentication_urls
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

class UpdateDatastore(webapp.RequestHandler):
    def get(self):
        logger.info("Enter Updating Datastote Task")

        slots = Slot.all()
        last_key = self.request.get('last_key', 'None')
        current_key = '0' 
        logger.info('---last %s', last_key)

        if last_key != 'None':
            last_key = db.Key(last_key)
            slots.filter('__key__ >=', last_key)
            current_key = last_key 

        slots.order('__key__')
        slots = slots.fetch(10)
        if len(slots) == 0:
            next_url = '/'
            last_key = '0'
        else:
            for slot in slots[:-1]:
                  slot.venue_key = str(slot.berth.bed.bedroom.venue.key())
                  slot.put()
            last_key = str(slots[-1].key())
            next_url = '/tasks/update_datastore?last_key=%s' % last_key
        logger.info("Exit adding Venue Key to Slot Task")

        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(
            PROJECT_PATH, 'templates', 'common', 'update_datastore.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text,
                                        'current_key': current_key,
                                        'next_url': next_url,
                                        }))


application = webapp.WSGIApplication([
      ('/tasks/expireenquiries', ExpireEnquiries),
      ('/tasks/emailguests', EmailGuests),
      ('/tasks/createslots', CreateSlotsTask),
      ('/tasks/update_datastore', UpdateDatastore),
      ], debug=False)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
