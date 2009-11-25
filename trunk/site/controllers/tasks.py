import os
import logging
from datetime import datetime
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.utils import get_authentication_urls
from models.bookinginfo import Enquiry

logger = logging.getLogger("Tasks")

class ClearExpireEnquiries(webapp.RequestHandler):
    def get(self):
        logger.info("Clear Expired Enquiries")
        enquiries = Enquiry.all()
        enquiries.filter('expiryDate !=', None)
        enquiries.filter('expiryDate <=', datetime.now())
        for enquiry in enquiries:
            logger.info("Expire enquiry -- %s", enquiry.referenceNumber)
            transitions = enquiry.getPossibleTransitions()
            for t in transitions:
                if t.startswith('expire'):
                    enquiry.doTransition(t)
                    break

        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 'templates', 'index.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


application = webapp.WSGIApplication([
      ('/tasks/clearexpiredenquiries', ClearExpireEnquiries),
      ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
