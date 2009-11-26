import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.match import MatchSchedule, CaptureMatch, EditMatch, DeleteMatch
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
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


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
          ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
