import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.client import ViewClient, CaptureClient, EditClient, DeleteClient
from controllers.address import CaptureAddress, EditAddress, DeleteAddress
from models.clientinfo import Client
from controllers.utils import get_authentication_urls


class ManageClients(webapp.RequestHandler):
    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        clients = Client.all().order('surname')
        filepath = os.path.join(PROJECT_PATH, 'templates', 'clients', 'manageclients.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'clients':clients,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

application = webapp.WSGIApplication([
                  ('/clients/clientinfo', ManageClients),
                  ('/clients/viewclient', ViewClient),
                  ('/clients/captureclient', CaptureClient),
                  ('/clients/editclient', EditClient),
                  ('/clients/deleteclient', DeleteClient),
                  ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()