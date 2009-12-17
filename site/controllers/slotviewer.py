import os
import urllib
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.utils import get_authentication_urls
from models.hostinfo import Venue, Slot

from controllers.utils import get_authentication_urls

logger = logging.getLogger('SlotViewer')

class ViewSlots(webapp.RequestHandler):
    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)

        query = Slot.all().order('__key__')
        size = int(self.request.get('size', '30'))
        start = self.request.get('start', 'None')
        if start != 'None':
          query.filter('__key__ >=', db.Key(start))
        slots = query.fetch(size+1)
        if slots:
            new_start = str(slots[-1].key())

        filepath = os.path.join(
            PROJECT_PATH, 'templates', 'admin', 'viewslots.html')
        context = {'base_path':BASE_PATH,
                  'auth_url':auth_url,
                  'auth_url_text':auth_url_text,
                  'size':size,
                  'start':new_start,
                  'slots':slots,
                  }
        self.response.out.write(template.render(filepath, context))




