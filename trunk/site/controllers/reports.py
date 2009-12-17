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
from models.reports import Report
from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.utils import get_authentication_urls
from controllers.date_utils import parse_datetime

class ViewReports(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                    'templates', 'admin', 'viewreports.html')
        rows= Report.all()
        report_names_dict = {}
        report_instances_dict = {}
        for row in rows:
            report_names_dict[row.name] = 'dummy'
            report_instances_dict[str(row.instance)] = 'dummy'
        report_names = report_names_dict.keys()
        report_name = self.request.get('report_name', None)
        if report_name is None and report_names:
            report_name = report_names[0]
        if report_name:
            rows.filter('name =', report_name)
                
        report_instances = report_instances_dict.keys()
        report_instance = self.request.get('report_instance', None)
        if report_instance is None and report_instances:
            report_instance = report_instances[0]
        if report_instance:
            rows.filter('instance =', 
                parse_datetime(report_instance, '%Y-%m-%d %H:%M:%S'))
        report_rows = [r.rowText for r in rows]
        self.response.out.write(template.render(filepath, 
                {
                    'base_path':BASE_PATH,
                    'auth_url':auth_url,
                    'auth_url_text':auth_url_text,
                    'report_names':report_names,
                    'report_instances':report_instances,
                    'report_name':report_name,
                    'report_instance':report_instance,
                    'report_rows':report_rows,
                    'user':users.get_current_user(),
                    'is_admin_user':users.is_current_user_admin(),
                    }))

    def post(self):
        report_name = self.request.get('report_name')
        report_instance = self.request.get('report_instance')
        refresh = self.request.get('refresh')
        if refresh:
            params = {}
            if report_name:
                params['report_name'] = report_name
            if report_instance:
                params['report_instance'] = report_instance
            params = urllib.urlencode(params)
            url = '/admin/reports/viewreports?%s' % params
            self.redirect(url)
            return
        self.redirect('/services/owner/viewreports')

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
        self.redirect('/admin/reports/viewreports')
