import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.clientinfo import Client
from controllers.utils import get_authentication_urls

logger = logging.getLogger('ClientHandler')


class ClientForm(djangoforms.ModelForm):

    class Meta:
        model = Client
        exclude = ['created', 'creator']


class ViewClient(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'clients', 'viewclient.html')
        clientkey = self.request.get('clientkey')
        client = Client.get(clientkey)
        form = ClientForm(instance=client)
        client_values = []
        for field in form.fields.keyOrder:
            for value in client.properties().values():
                if value.name == field:
                    name = value.name
                    if value.verbose_name:
                        name = value.verbose_name
                    val = value.get_value_for_form(client)
                    client_values.append((name, val))
        addresses = client.entity_addresses
        phonenumbers = client.entity_phonenumbers
        emails = client.entity_emails
        flights = client.client_flights
        matchtickets = client.client_matchtickets
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'client':client,
                                        'client_values':client_values,
                                        'addresses':addresses,
                                        'phonenumbers':phonenumbers,
                                        'emails':emails,
                                        'flights':flights,
                                        'matchtickets':matchtickets,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class CaptureClient(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'clients', 'captureclient.html')
        self.response.out.write(template.render(filepath, 
                        {
                            'base_path':BASE_PATH,
                            'form':ClientForm(),
                            'came_from':self.request.get('came_from'),
                            'auth_url':auth_url,
                            'auth_url_text':auth_url_text
                            }))

    def post(self):
        data = ClientForm(data=self.request.POST)
        came_from = self.request.get('came_from')
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.put()
            if came_from.startswith('/bookings/assignclient'):
                came_from = "%s&clientkey=%s" % (came_from, entity.key())
            self.redirect(came_from)
        else:
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'clients', 'captureclient.html')
            self.response.out.write(template.render(filepath, {'base_path':BASE_PATH,
                                                               'form':data
                                                               }))


class EditClient(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        clientkey = self.request.get('clientkey')
        client = Client.get(clientkey)
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'clients', 'editclient.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':ClientForm(instance=client),
                                        'clientkey':clientkey,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        clientkey = self.request.get('clientkey')
        client = Client.get(clientkey)
        data = ClientForm(data=self.request.POST, instance=client)
        if data.is_valid():
            entity = data.save(commit=False)
            #Extra work for non required date fields
            if not self.request.get('dateOfDate'):
                entity.dateOfDate = None
            #Change creator to last modified
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect('/clients/clientinfo')
        else:
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'clients', 'editclient.html')
            self.response.out.write(template.render(filepath, 
                                        {
                                            'base_path':BASE_PATH,
                                            'form':data,
                                            'clientkey':clientkey
                                            }))


class DeleteClient(webapp.RequestHandler):

    def get(self):
        clientkey = self.request.get('clientkey')
        client = Client.get(clientkey)
        if client:
            #recursive delete
            client.rdelete()

        self.redirect('/clients/clientinfo')

