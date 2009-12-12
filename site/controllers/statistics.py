import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.utils import get_authentication_urls, \
    listVenuesValidity, countAllEntities, checkBerths

logger = logging.getLogger('ViewStatistics')


class ViewStatistics(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'admin', 'viewstatistics.html')
        results = ''
        #results = 'Venue Completeness\n' + listVenuesValidity()
        results = 'Entity Count\n' + countAllEntities()
        #results = 'Check Berths\n' + checkBerths()
        self.response.out.write(template.render(filepath, 
                  {
                      'base_path':BASE_PATH,
                      'came_from':came_from,
                      'results':results,
                      'auth_url':auth_url,
                      'auth_url_text':auth_url_text
                      }))

