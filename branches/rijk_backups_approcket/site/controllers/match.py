import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from django import newforms as forms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.schedule import Match
from models.codelookup import getChoicesTuple
from controllers.utils import get_authentication_urls

logger = logging.getLogger('MatchHandler')


class MatchSchedule(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        matches = Match.all().order('number')
        filepath = os.path.join(PROJECT_PATH, 'templates', 'admin', 'matchschedule.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'matches':matches,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class MatchForm(djangoforms.ModelForm):
    class Meta:
        model = Match
        exclude = ['created', 'creator']

    city = forms.ChoiceField(choices=getChoicesTuple(('CTY')))

class CaptureMatch(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'admin', 'capturematch.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':MatchForm(),
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        data = MatchForm(data=self.request.POST)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                          'templates', 'admin', 'capturematch.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

class EditMatch(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        matchkey = self.request.get('matchkey')
        match = Match.get(matchkey)
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'admin', 'editmatch.html')
        self.response.out.write(template.render(filepath, 
                  {
                      'base_path':BASE_PATH,
                      'form':MatchForm(instance=match),
                      'matchkey':matchkey,
                      'came_from':came_from,
                      'auth_url':auth_url,
                      'auth_url_text':auth_url_text
                      }))

    def post(self):
        came_from = self.request.get('came_from')
        matchkey = self.request.get('matchkey')
        match = Match.get(matchkey)
        data = MatchForm(data=self.request.POST, instance=match)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                              'templates', 'admin', 'editmatch.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'matchkey':matchkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class DeleteMatch(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        key = self.request.get('matchkey')
        match = Match.get(key)
        if match:
            #recursive delete
            match.rdelete()
        self.redirect(came_from)


