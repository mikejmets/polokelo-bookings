import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from django import newforms as forms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.hostinfo import EmailAddress
from models.codelookup import getChoicesTuple
from controllers.utils import get_authentication_urls

logger = logging.getLogger('EmailAddressHandler')


class EmailForm(djangoforms.ModelForm):
    def __init__(self, *args, **kw):
        super(djangoforms.ModelForm, self).__init__(*args, **kw)
        self.fields.keyOrder = ['emailType', 'email']

    class Meta:
        model = EmailAddress
        exclude = ['created', 'creator', 'container']

    emailType = forms.ChoiceField(choices=getChoicesTuple(('EMLTP')))

class CaptureEmailAddress(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        containerkey = self.request.get('containerkey')
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'common', 'captureemail.html')
        self.response.out.write(template.render(filepath, 
                {
                    'base_path':BASE_PATH,
                    'form':EmailForm(),
                    'user':users.get_current_user(),
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
        data = EmailForm(data=self.request.POST)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.container = container
            entity._parent_key = containerkey
            entity._parent = container
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'common', 'captureemail.html')
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


class EditEmailAddress(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        came_from = self.request.referer
        emailkey = self.request.get('emailkey')
        emailaddress = EmailAddress.get(emailkey)
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'common', 'editemail.html')
        self.response.out.write(template.render(filepath, 
                {
                    'base_path':BASE_PATH,
                    'emailkey':emailkey,
                    'form':EmailForm(instance=emailaddress),
                    'came_from':came_from,
                    'post_url':self.request.uri,
                    'user':users.get_current_user(),
                    'auth_url':auth_url,
                    'auth_url_text':auth_url_text
                    }))

    def post(self):
        came_from = self.request.get('came_from')
        emailkey = self.request.get('emailkey')
        emailaddress = EmailAddress.get(emailkey)
        data = EmailForm(data=self.request.POST, instance=emailaddress)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity._parent_key = emailaddress.container.key()
            entity._parent = emailaddress.container
            entity.put()
            self.redirect(came_from)
        else:
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'common', 'editemail.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'emailkey':emailkey,
                                        'form':data,
                                        'came_from':came_from,
                                        'post_url':self.request.uri,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class DeleteEmailAddress(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        emailkey = self.request.get('emailkey')
        emailaddress = EmailAddress.get(emailkey)
        if emailaddress:
            #recursive delete
            emailaddress.rdelete()

        self.redirect(came_from)

