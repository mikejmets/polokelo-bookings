import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from django import newforms as forms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.roles import UserRole
from controllers.utils import get_authentication_urls
from models.codelookup import getChoicesTuple

logger = logging.getLogger('UserRoleHandler')


class UserRoleForm(djangoforms.ModelForm):

    class Meta:
        model = UserRole
        exclude = ['created', 'creator']

    role = forms.ChoiceField(choices=getChoicesTuple(('roles')))

class ViewUserRoles(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        userroles = UserRole.all().order('user')
        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'admin', 'viewuserroles.html')
        self.response.out.write(template.render(filepath, 
                {
                    'base_path':BASE_PATH,
                    'form':UserRoleForm(),
                    'came_from':came_from,
                    'userroles':userroles,
                    'user':users.get_current_user(),
                    'auth_url':auth_url,
                    'auth_url_text':auth_url_text
                    }))

class CaptureUserRole(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'admin', 'captureuserrole.html')
        self.response.out.write(template.render(filepath, 
                {
                    'base_path':BASE_PATH,
                    'form':UserRoleForm(),
                    'came_from':came_from,
                    'post_url':self.request.uri,
                    'user':users.get_current_user(),
                    'auth_url':auth_url,
                    'auth_url_text':auth_url_text
                    }))

    def post(self):
        came_from = self.request.get('came_from')
        data = UserRoleForm(data=self.request.POST)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'common', 'captureuserrole.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'came_from':came_from,
                                        'post_url':self.request.uri,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

class EditUserRole(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        userrolekey = self.request.get('userrolekey')
        userrole = UserRole.get(userrolekey)
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'common', 'edituserrole.html')
        self.response.out.write(template.render(filepath, 
                {
                    'base_path':BASE_PATH,
                    'form':UserRoleForm(instance=userrole),
                    'userrolekey':userrolekey,
                    'came_from':came_from,
                    'post_url':self.request.uri,
                    'user':users.get_current_user(),
                    'auth_url':auth_url,
                    'auth_url_text':auth_url_text
                    }))

    def post(self):
        came_from = self.request.get('came_from')
        userrolekey = self.request.get('userrolekey')
        userrole = UserRole.get(userrolekey)
        data = UserRoleForm(data=self.request.POST)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.put()
            userrole.delete()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'common', 'edituserrole.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'userrolekey':userrolekey,
                                        'came_from':came_from,
                                        'post_url':self.request.uri,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class DeleteUserRole(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        key = self.request.get('userrolekey')
        userrole = UserRole.get(key)
        if userrole:
            userrole.delete()
        self.redirect(came_from)

