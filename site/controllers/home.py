import os
import sys
import logging
from google.appengine.api import users, mail
from google.appengine.api.mail_errors import *
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app, login_required
from google.appengine.ext.webapp import template
from google.appengine.ext import db


PROJECT_PATH = os.path.join(os.path.dirname(__file__), '..')
BASE_PATH = os.path.join(PROJECT_PATH, 'templates', 'base.html')

def get_authentication_urls(dest_url):
    user = users.get_current_user()
    if user:
        return users.create_logout_url('/index'), 'Sign Out'
    else:
        return users.create_login_url(dest_url), 'Sign In'


class HomePage(webapp.RequestHandler):
    def get(self):
        logging.info('--------%s' % os.environ['CURRENT_VERSION_ID'])
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 'templates', 'index.html')
        self.response.out.write(template.render(filepath, 
                {
                    'base_path':BASE_PATH,
                    'user':users.get_current_user(),
                    'app_version': os.environ['CURRENT_VERSION_ID'],
                    'auth_url':auth_url,
                    'auth_url_text':auth_url_text
                    }))

class CommonError(webapp.RequestHandler):
    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(
            PROJECT_PATH, 'templates', 'common', 'commonerror.html')
        error = self.request.get('error')
        came_from = self.request.get('came_from')
        self.response.out.write(template.render(filepath, 
                {
                    'base_path':BASE_PATH,
                    'error':error,
                    'came_from':came_from,
                    'user':users.get_current_user(),
                    'auth_url':auth_url,
                    'auth_url_text':auth_url_text
                    }))

    def post(self):
        came_from = self.request.get('came_from')
        self.redirect(came_from)

application = webapp.WSGIApplication([
                            ('/', HomePage),
                            ('/index', HomePage),
                            ('/home/showerror', CommonError),
                            ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
