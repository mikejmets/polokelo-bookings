import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.hostinfo import Owner, Venue, Address
from controllers.utils import get_authentication_urls

logger = logging.getLogger('OwnerHandler')


class OwnerForm(djangoforms.ModelForm):
    #def __init__(self, *args, **kw):
    #  super(djangoforms.ModelForm, self).__init__(*args, **kw)
    #  self.fields.keyOrder = [
    #      'referenceNumber',
    #      'surname', 'firstNames', 'emailAddress', 'languages', 

    class Meta:
        model = Owner
        exclude = ['created', 'creator']

#from acl import Acl

class ViewOwner(webapp.RequestHandler):

    def get(self):
        #acl = Acl(area='ownerinfo',
        #          user=users.get_current_user())
        #assert acl.has_access(topic='ViewOwner', name='get') is True
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'viewowner.html')
        ownerkey = self.request.get('ownerkey')
        owner = Owner.get(ownerkey)
        form = OwnerForm(instance=owner)
        owner_values = []
        for field in form.fields.keyOrder:
            for value in owner.properties().values():
                if value.name == field:
                    name = value.name
                    if value.verbose_name:
                        name = value.verbose_name
                    val = value.get_value_for_form(owner)
                    owner_values.append((name, val))
        # venues = Venue.all().filter('owner = ', owner).order('name')
        venues = owner.owner_venues
        addresses = owner.entity_addresses
        phonenumbers = owner.entity_phonenumbers
        emails = owner.entity_emails
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'owner':owner,
                                        'owner_values':owner_values,
                                        'venues':venues,
                                        'addresses':addresses,
                                        'phonenumbers':phonenumbers,
                                        'emails':emails,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class CaptureOwner(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'captureowner.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':OwnerForm(),
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        data = OwnerForm(data=self.request.POST)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect('/services/hostinfo')
        else:
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'captureowner.html')
            self.response.out.write(template.render(filepath, {'base_path':BASE_PATH,
                                                               'form':data
                                                               }))


class EditOwner(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        ownerkey = self.request.get('ownerkey')
        owner = Owner.get(ownerkey)
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'editowner.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':OwnerForm(instance=owner),
                                        'ownerkey':ownerkey,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        ownerkey = self.request.get('ownerkey')
        owner = Owner.get(ownerkey)
        data = OwnerForm(data=self.request.POST, instance=owner)
        if data.is_valid():
            entity = data.save(commit=False)
            #Change creator to last modified
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect('/services/hostinfo')
        else:
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'editowner.html')
            self.response.out.write(template.render(filepath, 
                                        {
                                            'base_path':BASE_PATH,
                                            'form':data,
                                            'ownerkey':ownerkey
                                            }))


class DeleteOwner(webapp.RequestHandler):

    def get(self):
        ownerkey = self.request.get('ownerkey')
        owner = Owner.get(ownerkey)
        if owner:
            #recursive delete
            owner.rdelete()

        self.redirect('/services/hostinfo')

