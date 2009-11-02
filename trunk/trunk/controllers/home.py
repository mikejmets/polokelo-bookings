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


class HomePage(webapp.RequestHandler):
    def get(self):
        filepath = os.path.join(PROJECT_PATH, 'templates', 'index.html')
        self.response.out.write(template.render(filepath, {'base_path':BASE_PATH}))


application = webapp.WSGIApplication([
                            ('/', HomePage),
                            ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
