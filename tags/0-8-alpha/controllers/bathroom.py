import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.hostinfo import Bathroom
from controllers.utils import get_authentication_urls

logger = logging.getLogger('BathroomHandler')


class BathroomForm(djangoforms.ModelForm):
    class Meta:
        model = Bathroom
        exclude = ['created', 'creator', 'venue']


class CaptureBathroom(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        containerkey = self.request.get('containerkey')
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'capturebathroom.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':BathroomForm(),
                                        'containerkey':containerkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        data = BathroomForm(data=self.request.POST)
        containerkey = self.request.get('containerkey')
        container = db.Model.get(containerkey)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.venue = container
            entity._parent = container
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'capturebathroom.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'containerkey':containerkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

class EditBathroom(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        bathroomkey = self.request.get('bathroomkey')
        bathroom = Bathroom.get(bathroomkey)
        container = bathroom.venue
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'editbathroom.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':BathroomForm(instance=bathroom),
                                        'bathroomkey':bathroomkey,
                                        'containerkey': container.key,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        bathroomkey = self.request.get('bathroomkey')
        bathroom = Bathroom.get(bathroomkey)
        container = bathroom.venue
        data = BathroomForm(data=self.request.POST, instance=bathroom)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity._parent = container
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'editbathroom.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'bathroomkey':bathroomkey,
                                        'containerkey':container.key(),
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class DeleteBathroom(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        key = self.request.get('bathroomkey')
        bathroom = Bathroom.get(key)
        if bathroom:
            #recursive delete
            bathroom.rdelete()
        self.redirect(came_from)


