import os
import sys
import logging
import urllib
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import users

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.match import MatchSchedule, CaptureMatch, EditMatch, DeleteMatch
from models.hostinfo import Owner

from controllers.slotviewer import ViewSlots
from controllers.codelookup import \
    LookupTablesRoot, CaptureLookupTable, EditLookupTable, DeleteLookupTable, \
    ViewLookupTable, CaptureLookupItem, EditLookupItem, DeleteLookupItem
from controllers.packages import \
    PackageRoot, CapturePackage, EditPackage, DeletePackage
from controllers.statistics import ViewStatistics
from controllers.utils import get_authentication_urls
from models.schedule import Match


class AdminHomePage(webapp.RequestHandler):
    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 'templates', 'admin', 'adminhome.html')
        self.response.out.write(template.render(filepath, 
                {
                    'base_path':BASE_PATH,
                    'user':users.get_current_user(),
                    'auth_url':auth_url,
                    'auth_url_text':auth_url_text
                    }))

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
          ('/admin/slots/viewslots', ViewSlots),
          ], debug=False)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
