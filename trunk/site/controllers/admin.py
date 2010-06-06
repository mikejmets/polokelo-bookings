import os
import sys
import logging
import urllib
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.api.labs.taskqueue import Task

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.match import \
    MatchSchedule, CaptureMatch, EditMatch, DeleteMatch
from models.hostinfo import Owner, Venue

from controllers.slotviewer import ViewSlots
from controllers.codelookup import \
    LookupTablesRoot, CaptureLookupTable, EditLookupTable, DeleteLookupTable, \
    ViewLookupTable, CaptureLookupItem, EditLookupItem, DeleteLookupItem
from controllers.roles import \
    ViewUserRoles, CaptureUserRole, EditUserRole, DeleteUserRole
from controllers.packages import \
    PackageRoot, CapturePackage, EditPackage, DeletePackage
from controllers.statistics import ViewStatistics
from controllers.reports import ViewReports, VenueValidationReport
from controllers.utils import get_authentication_urls
from models.schedule import Match
from models.roles import UserRole


class AdminHomePage(webapp.RequestHandler):
    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 'templates', 'admin', 'adminhome.html')
        self.response.out.write(template.render(filepath, 
          {
              'base_path':BASE_PATH,
              'user':users.get_current_user(),
              'is_administrator': \
                  UserRole.hasRole(users.get_current_user(), 'Administrator'),
              'auth_url':auth_url,
              'auth_url_text':auth_url_text
              }))

class CreateSlots(webapp.RequestHandler):
    def get(self):

        #if not UserRole.hasRole(users.get_current_user(), 'Administrator'):
        #    return
        cnt = 0
        for venue in Venue.all().order('contractStartDate'):
            task = Task(
                method='GET',
                url='/tasks/createslots',
                params={'venuekey': venue.key()})
            task.add('slot-creation')
            logging.info('CreateSlotsTask: invoke venue %s', 
                venue.name)
            cnt += 1
              
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(
            PROJECT_PATH, 'templates', 'admin', 'adminhome.html')
        context = {'base_path':BASE_PATH,
                  'auth_url':auth_url,
                  'auth_url_text':auth_url_text,
                  }
        self.response.out.write(template.render(filepath, context))

class DeleteSlots(webapp.RequestHandler):
    def get(self):

        #if not UserRole.hasRole(users.get_current_user(), 'Administrator'):
        #    logging.info('DeleteSlots: not administrator')
        #    return
        cnt = 0
        for venue in Venue.all().order('contractStartDate'):
            task = Task(
                method='GET',
                url='/tasks/deleteslots',
                params={'venuekey': venue.key()})
            task.add('slot-deletion')
            logging.info('DeleteSlots: invoke venue %s', 
                venue.name)
            cnt += 1
              
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(
            PROJECT_PATH, 'templates', 'admin', 'adminhome.html')
        context = {'base_path':BASE_PATH,
                  'auth_url':auth_url,
                  'auth_url_text':auth_url_text,
                  }
        self.response.out.write(template.render(filepath, context))

class ClearData(webapp.RequestHandler):
    def get(self):
        error = None
        try:
          for owner in Owner.all().fetch(50):
                owner.rdelete()
        except:
            error = sys.exc_info()[1]

        params = {}
        if error is None:
            params = urllib.urlencode(params)
            self.redirect('/admin/home')
        else:
            params['error'] = error
            params = urllib.urlencode(params)
            self.redirect('/bookings/bookingerror?%s' % params)


application = webapp.WSGIApplication([
          ('/admin/home', AdminHomePage),
          ('/admin/schedule', MatchSchedule),
          ('/admin/schedule/capturematch', CaptureMatch),
          ('/admin/schedule/editmatch', EditMatch),
          ('/admin/schedule/deletematch', DeleteMatch),
          ('/admin/lookups', LookupTablesRoot),
          ('/admin/lookups/capturelookuptable', CaptureLookupTable),
          ('/admin/lookups/editlookuptable', EditLookupTable),
          ('/admin/lookups/deletelookuptable', DeleteLookupTable),
          ('/admin/lookups/viewlookuptable', ViewLookupTable),
          ('/admin/lookups/capturelookupitem', CaptureLookupItem),
          ('/admin/lookups/editlookupitem', EditLookupItem),
          ('/admin/lookups/deletelookupitem', DeleteLookupItem),
          ('/admin/statistics', ViewStatistics),
          ('/admin/packages', PackageRoot),
          ('/admin/packages/capturepackage', CapturePackage),
          ('/admin/packages/editpackage', EditPackage),
          ('/admin/packages/deletepackage', DeletePackage),
          ('/admin/reports/viewreports', ViewReports),
          ('/admin/reports/venuevalidationreport', VenueValidationReport),
          ('/admin/roles/viewuserroles', ViewUserRoles),
          ('/admin/roles/captureuserrole', CaptureUserRole),
          ('/admin/roles/deleteuserrole', DeleteUserRole),
          #('/admin/system/sysadmin', ViewSysAdmin),
          #('/admin/system/createslots', CreateSlots),
          ('/admin/slots/deleteslots', DeleteSlots),
          #('/admin/system/viewslots', ViewSlots),
          ], debug=False)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
