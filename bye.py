from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class ByePage(webapp.RequestHandler):
    def get(self):
        self.response.out.write("Bye-bye")


application = webapp.WSGIApplication([
                            ('/', ByePage),
                            ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
