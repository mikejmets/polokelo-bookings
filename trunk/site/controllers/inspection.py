import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.hostinfo import Inspection
from controllers.utils import get_authentication_urls

logger = logging.getLogger('InspectionHandler')


class InspectionForm(djangoforms.ModelForm):
    class Meta:
        model = Inspection
        exclude = ['created', 'creator', 'venue']


class CaptureInspection(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        containerkey = self.request.get('containerkey')
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'captureinspection.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':InspectionForm(),
                                        'containerkey':containerkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        data = InspectionForm(data=self.request.POST)
        containerkey = self.request.get('containerkey')
        container = db.Model.get(containerkey)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.venue = container
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'captureinspection.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'containerkey':containerkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

class EditInspection(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        inspectionkey = self.request.get('inspectionkey')
        inspection = Inspection.get(inspectionkey)
        container = inspection.venue
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'editinspection.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':InspectionForm(instance=inspection),
                                        'inspectionkey':inspectionkey,
                                        'containerkey': container.key,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        inspectionkey = self.request.get('inspectionkey')
        inspection = Inspection.get(inspectionkey)
        container = inspection.venue
        data = InspectionForm(data=self.request.POST, instance=inspection)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.container = container
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'editinspection.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'inspectionkey':inspectionkey,
                                        'containerkey':container.key(),
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class DeleteInspection(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        key = self.request.get('inspectionkey')
        inspection = Inspection.get(key)
        container = inspection.venue
        if inspection:
            # NOTE: obviously we will have to delete all venues 
            # and other related data before deleting the inspection
            inspection.delete()
        self.redirect(came_from)


