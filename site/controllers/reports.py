import os
import sys
import logging
import urllib
from datetime import datetime
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.api.labs.taskqueue import Task

from models.hostinfo import Owner, Venue
from models.roles import UserRole

class VenueValidationReport(webapp.RequestHandler):
    def get(self):

        if not UserRole.hasRole(users.get_current_user(), 'Administrator'):
            return
        report_name = 'VenueValidation'
        report_instance = str(datetime.now())
        params = {'reportname': report_name, 
                  'reportinstance': report_instance}
        cnt = 0
        for owner in Owner.all().order('referenceNumber'):
            venues = Venue.all()
            venues.filter('owner =', owner).order('contractStartDate')
            for venue in venues:
                params['venuekey'] = venue.key()
                params['split_report'] = True

                # Process just venue
                params['include_venue'] = True
                task = Task(
                    method='GET',
                    url='/tasks/venuevalidationreporttask', 
                    params=params)
                task.add('reporting')
                logging.info('VenueValidationReport: invoke venue %s', 
                    venue.name)

                # Proces just rooms
                for room in venue.venue_bedrooms:
                    params['bedroomkey'] = room.key()
                    params['include_rooms'] = True
                    task = Task(
                        method='GET',
                        url='/tasks/venuevalidationreporttask', 
                        params=params)
                    task.add('reporting')
                    logging.info('VenueValidationReport: invoke venue %s', 
                        venue.name)
            cnt += 1
            if cnt > 5:
                break
              
        params = {}
        params = urllib.urlencode(params)
        self.redirect('/admin/home')
