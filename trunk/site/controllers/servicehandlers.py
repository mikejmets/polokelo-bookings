import os
import sys
import logging
from google.appengine.api import users, mail
from google.appengine.api.mail_errors import *
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app, login_required
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

from controllers.home import BASE_PATH, PROJECT_PATH
from models.hostinfo import Owner


def get_authentication_urls(dest_url):
    user = users.get_current_user()
    if user:
        return users.create_logout_url('/index'), 'Sign Out'
    else:
        return users.create_login_url(dest_url), 'Sign In'


class ManageHosts(webapp.RequestHandler):
    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        partners = Owner.all().order('surname')
        filepath = os.path.join(PROJECT_PATH, 'templates', 'services', 'managehosts.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'partners':partners,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class OwnerForm(djangoforms.ModelForm):
    class Meta:
        model = Owner
        exclude = ['created', 'creator']


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


application = webapp.WSGIApplication([
                            ('/services/hostinfo', ManageHosts),
                            ('/services/captureowner', CaptureOwner),
                            ('/services/editowner', EditOwner),
                            ('/services/deleteowner', DeleteOwner),
                            ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()