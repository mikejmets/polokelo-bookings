import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.hostinfo import PhoneNumber
from controllers.utils import get_authentication_urls

logger = logging.getLogger('PhoneNumberHandler')


class PhoneNumberForm(djangoforms.ModelForm):
    def __init__(self, *args, **kw):
        super(djangoforms.ModelForm, self).__init__(*args, **kw)
        self.fields.keyOrder = ['numberType', 'number']

    class Meta:
        model = PhoneNumber
        exclude = ['created', 'creator', 'container']


class CapturePhoneNumber(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        containerkey = self.request.get('containerkey')
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'common', 'capturephonenumber.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':PhoneNumberForm(),
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text,
                                        'came_from':came_from,
                                        'post_url':self.request.uri,
                                        'containerkey':containerkey
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        containerkey = self.request.get('containerkey')
        container = db.Model.get(containerkey)
        data = PhoneNumberForm(data=self.request.POST)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.container = container
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'common', 'capturephonenumber.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text,
                                        'form':data,
                                        'came_from':came_from,
                                        'post_url':self.request.uri,
                                        'containerkey':containerkey
                                        }))


class EditPhoneNumber(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        came_from = self.request.referer
        phonekey = self.request.get('phonekey')
        phonenumber = PhoneNumber.get(phonekey)
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'common', 'editphonenumber.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'phonekey':phonekey,
                                        'form':PhoneNumberForm(instance=phonenumber),
                                        'came_from':came_from,
                                        'post_url':self.request.uri,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        phonekey = self.request.get('phonekey')
        phonenumber = PhoneNumber.get(phonekey)
        data = PhoneNumberForm(data=self.request.POST, instance=phonenumber)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect(came_from)
        else:
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'common', 'editphonenumber.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'phonekey':phonekey,
                                        'form':data,
                                        'came_from':came_from,
                                        'post_url':self.request.uri,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class DeletePhoneNumber(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        phonekey = self.request.get('phonekey')
        phonenumber = PhoneNumber.get(phonekey)
        if phonenumber:
            #recursive delete
            phonenumber.rdelete()

        self.redirect(came_from)

