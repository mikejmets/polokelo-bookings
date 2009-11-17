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

class ViewBedroom(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'viewbedroom.html')
        bedroomkey = self.request.get('bedroomkey')
        bedroom = Bedroom.get(bedroomkey)
        form = BedroomForm(instance=bedroom)
        bedroom_values = []
        for field in form.fields.keyOrder:
            for value in bedroom.properties().values():
                if value.name == field:
                    name = value.name
                    if value.verbose_name:
                        name = value.verbose_name
                    val = value.get_value_for_form(bedroom)
                    bedroom_values.append((name, val))
        beds = bedroom.bedroom_beds
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':BedroomForm(),
                                        'bedroom':bedroom,
                                        'bedroom_values':bedroom_values,
                                        'beds':beds,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text,
                                        'venuekey':self.request.get('venuekey')
                                        }))

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
            entity._parent = container
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
                                        'auth_url_text':auth_url_text,
                                        'venuekey':self.request.get('venuekey')
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        bedroomkey = self.request.get('bedroomkey')
        bedroom = Bedroom.get(bedroomkey)
        data = BedroomForm(data=self.request.POST, instance=bedroom)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect(came_from)
        else:
            container = bedroom.venue
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
        if bedroom:
            #recursive delete
            bedroom.rdelete()
        self.redirect(came_from)


