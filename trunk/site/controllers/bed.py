import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.hostinfo import Bed, Berth
from controllers.utils import get_authentication_urls

logger = logging.getLogger('BedHandler')


class BedForm(djangoforms.ModelForm):
    class Meta:
        model = Bed
        exclude = ['created', 'creator', 'bedroom']


class CaptureBed(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        containerkey = self.request.get('containerkey')
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'capturebed.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':BedForm(),
                                        'containerkey':containerkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        data = BedForm(data=self.request.POST)
        containerkey = self.request.get('containerkey')
        container = db.Model.get(containerkey)
        if data.is_valid():
            bed = data.save(commit=False)
            bed.creator = users.get_current_user()
            bed.bedroom = container
            bed._parent = container
            bed.put()
            #Auto create a berth per capacity
            for i in range(bed.capacity):
                berth = Berth(parent=bed)
                berth.creator = users.get_current_user()
                berth.bed = bed
                berth.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'capturebed.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'containerkey':containerkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

class EditBed(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        bedkey = self.request.get('bedkey')
        bed = Bed.get(bedkey)
        container = bed.bedroom
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'editbed.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':BedForm(instance=bed),
                                        'bedkey':bedkey,
                                        'containerkey': container.key,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        bedkey = self.request.get('bedkey')
        bed = Bed.get(bedkey)
        data = BedForm(data=self.request.POST, instance=bed)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect(came_from)
        else:
            container = bed.bedroom
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'editbed.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'bedkey':bedkey,
                                        'containerkey':container.key(),
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class DeleteBed(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        key = self.request.get('bedkey')
        bed = Bed.get(key)
        if bed:
            #recursive delete
            bed.rdelete()
        self.redirect(came_from)


