import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from django import newforms as forms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.hostinfo import Bed, Berth
from controllers.utils import get_authentication_urls
from models.codelookup import getChoicesTuple

logger = logging.getLogger('BerthHandler')


class BerthForm(djangoforms.ModelForm):
    class Meta:
        model = Bed
        exclude = ['created', 'creator']

class ViewBerth(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        berthkey = self.request.get('berthkey')
        berth = Berth.get(berthkey)
        bed = berth.bed
        form = BerthForm(instance=berth)
        berth_values = [('Key', berthkey),]
        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'services', 'viewberth.html')
        self.response.out.write(template.render(filepath, 
                {
                    'base_path':BASE_PATH,
                    'form':BerthForm(),
                    'berth_values':berth_values,
                    'bedkey':bed.key(),
                    'slots':berth.berth_slots.order('startDate'),
                    'came_from':came_from,
                    'auth_url':auth_url,
                    'auth_url_text':auth_url_text
                    }))

