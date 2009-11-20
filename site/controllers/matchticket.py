import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.clientinfo import MatchTicket
from controllers.utils import get_authentication_urls

logger = logging.getLogger('MatchTicketHandler')


class MatchTicketForm(djangoforms.ModelForm):
    class Meta:
        model = MatchTicket
        exclude = ['created', 'creator']


class CaptureMatchTicket(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        containerkey = self.request.get('containerkey')
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'clients', 'capturematchticket.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':MatchTicketForm(),
                                        'containerkey':containerkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        data = MatchTicketForm(data=self.request.POST)
        containerkey = self.request.get('containerkey')
        container = db.Model.get(containerkey)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity._parent_key = containerkey
            entity._parent = container
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                          'templates', 'clients', 'capturematchticket.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'containerkey':containerkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

class EditMatchTicket(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        matchticketkey = self.request.get('matchticketkey')
        matchticket = MatchTicket.get(matchticketkey)
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'clients', 'editmatchticket.html')
        self.response.out.write(template.render(filepath, 
                  {
                      'base_path':BASE_PATH,
                      'form':MatchTicketForm(instance=matchticket),
                      'matchticketkey':matchticketkey,
                      'came_from':came_from,
                      'auth_url':auth_url,
                      'auth_url_text':auth_url_text
                      }))

    def post(self):
        came_from = self.request.get('came_from')
        matchticketkey = self.request.get('matchticketkey')
        matchticket = MatchTicket.get(matchticketkey)
        data = MatchTicketForm(data=self.request.POST, instance=matchticket)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                              'templates', 'clients', 'editmatchticket.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'matchticketkey':matchticketkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class DeleteMatchTicket(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        key = self.request.get('matchticketkey')
        matchticket = MatchTicket.get(key)
        if matchticket:
            #recursive delete
            matchticket.rdelete()
        self.redirect(came_from)


