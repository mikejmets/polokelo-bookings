import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.hostinfo import Bedroom
from controllers.utils import get_authentication_urls

logger = logging.getLogger('BedroomHandler')


class BedroomForm(djangoforms.ModelForm):
    class Meta:
        model = Bedroom
        exclude = ['created', 'creator', 'venue']


class CaptureBedroom(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        containerkey = self.request.get('containerkey')
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'capturebedroom.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':BedroomForm(),
                                        'containerkey':containerkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        data = BedroomForm(data=self.request.POST)
        containerkey = self.request.get('containerkey')
        container = db.Model.get(containerkey)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.venue = container
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'capturebedroom.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'containerkey':containerkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

class EditBedroom(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        bedroomkey = self.request.get('bedroomkey')
        bedroom = Bedroom.get(bedroomkey)
        container = bedroom.venue
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'editbedroom.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':BedroomForm(instance=bedroom),
                                        'bedroomkey':bedroomkey,
                                        'containerkey': container.key,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        bedroomkey = self.request.get('bedroomkey')
        bedroom = Bedroom.get(bedroomkey)
        container = bedroom.venue
        data = BedroomForm(data=self.request.POST, instance=bedroom)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.container = container
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'editbedroom.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'bedroomkey':bedroomkey,
                                        'containerkey':container.key(),
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class DeleteBedroom(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        key = self.request.get('bedroomkey')
        bedroom = Bedroom.get(key)
        container = bedroom.venue
        if bedroom:
            # NOTE: obviously we will have to delete all venues 
            # and other related data before deleting the bedroom
            bedroom.delete()
        self.redirect(came_from)


