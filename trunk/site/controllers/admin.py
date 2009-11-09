import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.match import CaptureMatch, EditMatch, DeleteMatch
from controllers.utils import get_authentication_urls
from models.schedule import Match


class AdminHomePage(webapp.RequestHandler):
    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        matches = Match.all().order('number')
        filepath = os.path.join(PROJECT_PATH, 'templates', 'admin', 'adminhome.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'matches':matches,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


application = webapp.WSGIApplication([
                            ('/admin/home', AdminHomePage),
                            ('/admin/schedule/capturematch', CaptureMatch),
                            ('/admin/schedule/editmatch', EditMatch),
                            ('/admin/schedule/deletematch', DeleteMatch),
                            ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
