import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.owner import CaptureAddress, EditAddress, DeleteAddress
from controllers.owner import ViewOwner, CaptureOwner, EditOwner, DeleteOwner
from controllers.venue import CaptureVenue, EditVenue, DeleteVenue
from models.hostinfo import Owner
from controllers.utils import get_authentication_urls

class ManageHosts(webapp.RequestHandler):
    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        partners = Owner.all().order('surname')
        filepath = os.path.join(PROJECT_PATH, 'templates', 'services', 'managehosts.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'partners':partners,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

application = webapp.WSGIApplication([
                            ('/services/hostinfo', ManageHosts),
                            ('/services/viewowner', ViewOwner),
                            ('/services/captureowner', CaptureOwner),
                            ('/services/editowner', EditOwner),
                            ('/services/deleteowner', DeleteOwner),
                            ('/services/owner/captureaddress', CaptureAddress),
                            ('/services/owner/editaddress', EditAddress),
                            ('/services/owner/deleteaddress', DeleteAddress),
                            ('/services/owner/capturevenue', CaptureVenue),
                            ('/services/owner/editvenue', EditVenue),
                            ('/services/owner/deletevenue', DeleteVenue),
                            ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
