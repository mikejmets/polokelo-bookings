import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms

from controllers.home import BASE_PATH, PROJECT_PATH
from models.hostinfo import Owner, Venue
from controllers.utils import get_authentication_urls

logger = logging.getLogger('VenueHandler')


class VenueForm(djangoforms.ModelForm):
    class Meta:
        model = Venue
        exclude = ['owner', 'created', 'creator']

class ViewVenue(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'viewvenue.html')
        venuekey = self.request.get('venuekey')
        venue = Venue.get(venuekey)
        form = VenueForm(instance=venue)
        venue_values = []
        for field in form.fields.keyOrder:
            for value in venue.properties().values():
                if value.name == field:
                    name = value.name
                    if value.verbose_name:
                        name = value.verbose_name
                    val = value.get_value_for_form(venue)
                    venue_values.append((name, val))
        addresses = venue.entity_addresses
        phonenumbers = venue.entity_phonenumbers
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'venue':venue,
                                        'venue_values':venue_values,
                                        'addresses':addresses,
                                        'phonenumbers':phonenumbers,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class CaptureVenue(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                                  'templates', 'services', 'capturevenue.html')
        ownerkey = self.request.get('ownerkey')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':VenueForm(),
                                        'ownerkey':ownerkey,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        data = VenueForm(data=self.request.POST)
        ownerkey = self.request.get('ownerkey')
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.owner = Owner.get(ownerkey)
            entity.put()
            self.redirect('/services/viewowner?ownerkey=%s' % ownerkey)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'capturevenue.html')
            self.response.out.write(template.render(filepath, 
                      {'base_path':BASE_PATH,
                       'form':data,
                       'ownerkey':ownerkey,
                       'auth_url':auth_url,
                       'auth_url_text':auth_url_text
                                               }))


class EditVenue(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        venuekey = self.request.get('venuekey')
        ownerkey = self.request.get('ownerkey')
        venue = Venue.get(venuekey)
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'editvenue.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':VenueForm(instance=venue),
                                        'venuekey':venuekey,
                                        'ownerkey':ownerkey,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        venuekey = self.request.get('venuekey')
        venue = Venue.get(venuekey)
        ownerkey = self.request.get('ownerkey')
        data = VenueForm(data=self.request.POST, instance=venue)
        if data.is_valid():
            entity = data.save(commit=False)
            #Change creator to last modified
            entity.owner = Owner.get(ownerkey)
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect('/services/viewowner?ownerkey=%s' % ownerkey)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'editvenue.html')
            self.response.out.write(template.render(filepath, 
                                        {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'venuekey':venuekey,
                                        'ownerkey':ownerkey,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class DeleteVenue(webapp.RequestHandler):

    def get(self):
        ownerkey = self.request.get('ownerkey')
        venuekey = self.request.get('venuekey')
        venue = Venue.get(venuekey)
        if venue:
            # NOTE: obviously we will have to delete all venues 
            # and other related data before deleting the venue
            venue.delete()

        self.redirect('/services/viewowner?ownerkey=%s' % ownerkey)

