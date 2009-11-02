import cgi
import os
from google.appengine.api import users, images
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db
import populate

from model import ArtWork


class AdminHomePage(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'admin', 'admin.html')
        self.response.out.write(template.render(path, {}))


application = webapp.WSGIApplication([
                            ('/admin/home', AdminHomePage),
                            ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
