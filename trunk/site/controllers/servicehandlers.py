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

class ManageHosts(webapp.RequestHandler):
    def get(self):
        partners = Owner.all().order('surname')
        filepath = os.path.join(PROJECT_PATH, 'templates', 'services', 'managehosts.html')
        self.response.out.write(template.render(filepath, {'base_path':BASE_PATH,
                                                           'partners':partners 
                                                           }))


class OwnerForm(djangoforms.ModelForm):
    class Meta:
        model = Owner
        exclude = ['created', 'creator']

class CaptureOwner(webapp.RequestHandler):

    def get(self):
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'captureowner.html')
        self.response.out.write(template.render(filepath, {'base_path':BASE_PATH,
                                                           'form':OwnerForm(),
                                                           }))

    def post(self):
        data = OwnerForm(data = self.request.POST)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect('/services/index')
        else:
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'captureowner.html')
            self.response.out.write(template.render(filepath, {'base_path':BASE_PATH,
                                                               'form':data
                                                               }))


application = webapp.WSGIApplication([
                            ('/services/index', ManageHosts),
                            ('/services/captureowner', CaptureOwner),
                            ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
