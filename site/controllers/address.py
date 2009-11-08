import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.hostinfo import Address
from controllers.utils import get_authentication_urls

logger = logging.getLogger('AddressHandler')


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
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        containerkey = self.request.get('containerkey')
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'common', 'captureaddress.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':AddressForm(),
                                        'containerkey':containerkey,
                                        'came_from':came_from,
                                        'post_url':self.request.uri,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        data = AddressForm(data=self.request.POST)
        containerkey = self.request.get('containerkey')
        container = db.Model.get(containerkey)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.container = container
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'common', 'captureaddress.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'containerkey':containerkey,
                                        'came_from':came_from,
                                        'post_url':self.request.uri,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

class EditAddress(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        addresskey = self.request.get('addresskey')
        address = Address.get(addresskey)
        container = address.container
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'common', 'editaddress.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':AddressForm(instance=address),
                                        'addresskey':addresskey,
                                        'containerkey': container.key,
                                        'came_from':came_from,
                                        'post_url':self.request.uri,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        addresskey = self.request.get('addresskey')
        address = Address.get(addresskey)
        container = address.container
        data = AddressForm(data=self.request.POST, instance=address)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.container = container
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'common', 'editaddress.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'addresskey':addresskey,
                                        'containerkey':container.key(),
                                        'came_from':came_from,
                                        'post_url':self.request.uri,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class DeleteAddress(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        key = self.request.get('addresskey')
        address = Address.get(key)
        container = address.container
        if address:
            #recursive delete
            address.rdelete()
        self.redirect(came_from)


