import os
import logging
from datetime import datetime
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api.labs.taskqueue import Task

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.utils import get_authentication_urls
from controllers.date_utils import parse_datetime
from models.bookinginfo import Enquiry
from models.hostinfo import Owner, Venue, Slot, Bed, Berth

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
        venuekey = self.request.get('venuekey')
        logger.info('CreateSlotsTask got key %s', venuekey)
        if venuekey:
            venue = Venue.get(venuekey)
            if venue:
                try:
                    limit = 20
                    num_slots = venue.createSlots(limit=limit)
                    if num_slots >= limit:
                        #Create task to continue
                        task = Task(
                            method='GET',
                            url='/tasks/createslots',
                            params={'venuekey': venue.key()})
                        task.add('slot-creation')
                        logger.info('CreateSlotsTask again, venue %s = %s', 
                            venue.name, num_slots)
                except DeadlineExceededError:
                    self.response.clear()
                    self.response.set_status(500)
                    logger.error("Except DeadlineExceeded for venue %s",
                        "%s %s" % (venue.owner.referenceNumber, venue.name))
                except Exception, e:
                    self.response.clear()
                    self.response.set_status(500)
                    logger.error("Except %s Error for venue %s",
                        e,
                        "%s %s" % (venue.owner.referenceNumber, venue.name))

        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 'templates', 'index.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

class CreateBerthSlots(webapp.RequestHandler):
    def get(self):
        berths = Berth.all().order('created')
        last_key = self.request.get('last_key', 'None')

        if last_key != 'None':
            last_key = parse_datetime(
                last_key, '%Y-%m-%d %H:%M:%S')
            berths.filter('created >=', last_key)
            logger.info("Create Slots for berth from %s", last_key)

        report = ""
        berths = berths.fetch(5)
        if len(berths) == 0:
            next_url = '/'
            last_key = '0'
            report += "The End\n"
        else:
            cnt = 0
            for i in range(0, min(len(berths), 4)):
                cnt += berths[i].createSlots()
                report += "created slots date %s (indx = %s cnt = %s)\n" % (
                    berths[i].created, i, cnt)
                if cnt > 20:
                    break
            last_key = berths[i].created
            next_url = '/tasks/createberthslots?last_key=%s' % str(last_key)

        context = {
                  'next_url': next_url,
                  'report': report,
                  }
        self.response.out.write(context) 

class DeleteBerthSlots(webapp.RequestHandler):
    def get(self):
        # Delete first and then recreate all slots
        report = 'Ooops'
        berths = Berth.all().order('created')
        last_key = self.request.get('last_key', 'None')
        action = self.request.get('action', 'delete')
        limit = int(self.request.get('limit', '2'))

        report = ""
        if last_key != 'None':
            last_key = parse_datetime(
                last_key, '%Y-%m-%d %H:%M:%S')
            berths.filter('created >=', last_key)
        berths = berths.fetch(limit=limit)
        cnt = 0
        for berth in berths:
            cnt += 1
            if cnt == limit:
                break
            for slot in Slot.all().ancestor(berth):
               slot.delete()
            report += "delete berth slots date %s (cnt = %s)\n" % (
               berth.created, cnt)
        last_key = berth.created
        if len(berths) == 1:
            action = 'stop'
            last_key = 'None'
            report += "The End\n"

        context = {
                  'action': action,
                  'last_key': str(last_key),
                  'report': report,
                  }
        self.response.out.write(context) 

class BedValidation(webapp.RequestHandler):
    def get(self):
        beds = Bed.all().order('created')
        last_key = self.request.get('last_key', 'None')

        if last_key != 'None':
            last_key = parse_datetime(
                last_key, '%Y-%m-%d %H:%M:%S')
            beds.filter('created >', last_key)
            logger.info("Create Slots for berth from %s", last_key)

        report = ""
        beds = beds.fetch(limit=10)
        if len(beds) == 0:
            next_url = '/'
            last_key = '0'
        else:
            for bed in beds:
                try:
                    room = bed.bedroom
                    venue = room.venue
                except Exception, e:
                    report += '---room problem--%s: %s' % (
                        bed.key(),
                        e)
                    if str(e).startswith('ReferenceProperty fail'):
                        bed.rdelete()
                    continue
                if bed.name is None or len(bed.name) == 0:
                    bed.name = '1'
                    report += 'Set Name: Owner %s Venue %s Room %s Bed %s' % (
                        venue.owner.referenceNumber,
                        venue.name,
                        room.name,
                        bed.name)

                if not bed.isValid():
                    # Report, delete and recreate
                    report += 'Invalid: Owner %s Venue %s Room %s Bed %s' % (
                        venue.owner.referenceNumber,
                        venue.name,
                        room.name,
                        bed.name)
                    for berth in bed.bed_berths:
                        berth.rdelete()
                    bed.createBerths()

            last_key = beds[-1].created
            next_url = '/tasks/bedvalidation?last_key=%s' % str(last_key)

        context = {
                  'next_url': next_url,
                  'report': report,
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

        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        context = {
                  'base_path':BASE_PATH,
                  'auth_url':auth_url,
                  'auth_url_text':auth_url_text,
                  'next_url': next_url,
                  }
        self.response.out.write(context) 

class VenueValidation(webapp.RequestHandler):
    def get(self):
        owners = Owner.all()
        owners.order('referenceNumber')
        last = self.request.get('last', 'None')

        if last != 'None':
            logger.info('-----last %s', last)
            owners.filter('referenceNumber >', last)

        owner = owners.get()
        if owner:
            last = owner.referenceNumber
            report = ""
            for venue in owner.owner_venues:
                report += "%s %s Status %s Is Valid %s\n" % (
                    owner.referenceNumber, venue.name, 
                    venue.state, venue.isValid())
            context = {
                      'last': last,
                      'report':report,
                      }
        else:
            context = {
                      'last': '0',
                      'report':'The End',
                      }

        self.response.out.write(context) 

application = webapp.WSGIApplication([
      ('/tasks/expireenquiries', ExpireEnquiries),
      ('/tasks/emailguests', EmailGuests),
      ('/tasks/createslots', CreateSlotsTask),
      ('/tasks/createberthslots', CreateBerthSlots),
      ('/tasks/deleteberthslots', DeleteBerthSlots),
      ('/tasks/update_datastore', UpdateDatastore),
      ('/tasks/bedvalidation', BedValidation),
      ('/tasks/venuevalidation', VenueValidation),
      ], debug=False)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
