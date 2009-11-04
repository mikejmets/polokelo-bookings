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
    def __init__(self, *args, **kw):
      super(djangoforms.ModelForm, self).__init__(*args, **kw)
      self.fields.keyOrder = [
          'referenceNumber',
          'surname', 'firstNames', 'emailAddress', 'languages', 
          'addendumADate', 'addendumBDate', 'addendumCDate', 'trainingSession',]

    class Meta:
        model = Owner
        exclude = ['created', 'creator']


class ViewOwner(webapp.RequestHandler):

    def get(self):
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
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'owner':owner,
                                        'owner_values':owner_values,
                                        'venues':venues,
                                        'addresses':addresses,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class AddressForm(djangoforms.ModelForm):
    def __init__(self, *args, **kw):
      super(djangoforms.ModelForm, self).__init__(*args, **kw)
      self.fields.keyOrder = [
            'addressType', 'streetAddress', 'suburb',
            'city', 'country', 'postCode'
          ]

    class Meta:
        model = Address
        exclude = ['created', 'creator', 'container']


class CaptureAddress(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        ownerkey = self.request.get('ownerkey')
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'captureaddress.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':AddressForm(),
                                        'ownerkey':ownerkey,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        data = AddressForm(data=self.request.POST)
        ownerkey = self.request.get('ownerkey')
        owner = db.Model.get(ownerkey)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.container = owner
            entity.put()
            self.redirect('/services/viewowner?ownerkey=%s' % ownerkey)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'captureaddress.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'ownerkey':ownerkey,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

class EditAddress(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        addresskey = self.request.get('addresskey')
        address = Address.get(addresskey)
        owner = address.container
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'editaddress.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':AddressForm(instance=address),
                                        'addresskey':addresskey,
                                        'ownerkey': owner.key,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        addresskey = self.request.get('addresskey')
        address = Address.get(addresskey)
        owner = address.container
        data = AddressForm(data=self.request.POST, instance=address)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.container = owner
            entity.put()
            self.redirect('/services/viewowner?ownerkey=%s' % owner.key())
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'editaddress.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'ownerkey':owner.key(),
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class DeleteAddress(webapp.RequestHandler):

    def get(self):
        key = self.request.get('addresskey')
        address = Address.get(key)
        owner = address.container
        if address:
            # NOTE: obviously we will have to delete all venues 
            # and other related data before deleting the address
            address.delete()
            self.redirect('/services/viewowner?ownerkey=%s' % owner.key())


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
            #Extra work for non required date fields
            if not self.request.get('addendumADate'):
                entity.addendumADate = None
            if not self.request.get('addendumBDate'):
                entity.addendumBDate = None
            if not self.request.get('addendumCDate'):
                entity.addendumCDate = None
            if not self.request.get('addendumADate'):
                entity.addendumADate = None
            if not self.request.get('trainingSession'):
                entity.trainingSession = None
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
            # NOTE: obviously we will have to delete all venues 
            # and other related data before deleting the owner
            owner.delete()

        self.redirect('/services/hostinfo')

