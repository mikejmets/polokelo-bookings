import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.client import ViewClient, CaptureClient, EditClient, DeleteClient
from controllers.address import CaptureAddress, EditAddress, DeleteAddress
from controllers.phonenumber \
        import CapturePhoneNumber, EditPhoneNumber, DeletePhoneNumber
from controllers.emailaddress \
        import CaptureEmailAddress, EditEmailAddress, DeleteEmailAddress
from controllers.flight \
        import CaptureFlight, EditFlight, DeleteFlight
from controllers.matchticket \
        import CaptureMatchTicket, EditMatchTicket, DeleteMatchTicket
from models.clientinfo import Client
from controllers.utils import get_authentication_urls


class ManageClients(webapp.RequestHandler):
    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        clients = Client.all().order('surname')
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'clients', 'manageclients.html')
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
      ('/clients/address/captureaddress', CaptureAddress),
      ('/clients/address/editaddress', EditAddress),
      ('/clients/address/deleteaddress', DeleteAddress),
      ('/clients/email/captureemail', CaptureEmailAddress),
      ('/clients/email/editemail', EditEmailAddress),
      ('/clients/email/deleteemail', DeleteEmailAddress),
      ('/clients/contact/capturephone', CapturePhoneNumber),
      ('/clients/contact/editphone', EditPhoneNumber),
      ('/clients/contact/deletephone', DeletePhoneNumber),
      ('/clients/flight/captureflight', CaptureFlight),
      ('/clients/flight/editflight', EditFlight),
      ('/clients/flight/deleteflight', DeleteFlight),
      ('/clients/matchticket/capturematchticket', CaptureMatchTicket),
      ('/clients/matchticket/editmatchticket', EditMatchTicket),
      ('/clients/matchticket/deletematchticket', DeleteMatchTicket),
      ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
