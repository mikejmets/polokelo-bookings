import os
import logging
import urllib
from datetime import datetime, timedelta
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.runtime import DeadlineExceededError
from google.appengine.ext.db import djangoforms
from google.appengine.api.labs.taskqueue import Task
from django import newforms as forms

from controllers.home import BASE_PATH, PROJECT_PATH
from models.bookinginfo import ContractedBooking
from models.services import ServiceProvider, Service
from models.codelookup import getChoicesTuple
from controllers.utils import get_authentication_urls

logger = logging.getLogger('ServiceHandler')


class ServiceForm(djangoforms.ModelForm):
    class Meta:
        model = Service
        exclude = ['created', 'creator']


class ViewService(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'services', 'viewservice.html')
        
        servicekey = self.request.get('servicekey')
        service = Service.get(servicekey)
        form = ServiceForm(instance=service)
        service_values = []
        for field in form.fields.keyOrder:
            for value in service.properties().values():
                if value.name == field:
                    name = value.name
                    if value.verbose_name:
                        name = value.verbose_name
                    val = value.get_value_for_form(service)
                    service_values.append((name, val))
        context = {}

        addresses = service.entity_addresses
        phonenumbers = service.entity_phonenumbers
        emails = service.entity_emails
        context['came_from'] = self.request.referer
        context['addresses'] = addresses
        context['base_path'] = BASE_PATH
        context['service'] = service
        context['service_values'] = service_values
        context['phonenumbers'] = phonenumbers
        context['emails'] = emails
        context['user'] = users.get_current_user()
        context['is_admin_user'] = users.is_current_user_admin()
        context['auth_url'] = auth_url
        context['auth_url_text'] = auth_url_text

        self.response.out.write(template.render(filepath, context))


class CaptureService(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                                  'templates', 'services', 'captureservice.html')
        providerkey = self.request.get('providerkey')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':ServiceForm(),
                                        'providerkey':providerkey,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        logger.info('In')
        data = ServiceForm(data=self.request.POST)
        providerkey = self.request.get('providerkey')
        provider = ServiceProvider.get(providerkey)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity._parent_key = providerkey
            entity._parent = provider
            entity.put()
            self.redirect('/services/provider/viewprovider?providerkey=%s' \
                % providerkey)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                          'templates', 'services', 'captureservice.html')
            self.response.out.write(template.render(filepath, 
                      {'base_path':BASE_PATH,
                       'form':data,
                       'providerkey':providerkey,
                       'auth_url':auth_url,
                       'auth_url_text':auth_url_text
                                               }))


class EditService(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        servicekey = self.request.get('servicekey')
        service = Service.get(servicekey)
        providerkey = self.request.get('providerkey')
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'editservice.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':ServiceForm(instance=service),
                                        'servicekey':servicekey,
                                        'providerkey':providerkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        servicekey = self.request.get('servicekey')
        service = Service.get(servicekey)
        data = ServiceForm(data=self.request.POST, instance=service)
        if data.is_valid():
            entity = data.save(commit=False)
            if not self.request.get('contractStartDate'):
                entity.contractStartDate = None
            if not self.request.get('contractEndDate'):
                entity.contractEndDate = None
            #Change creator to last modified
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'editservice.html')
            self.response.out.write(template.render(filepath, 
                                        {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'servicekey':servicekey,
                                        'providerkey':providerkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class DeleteService(webapp.RequestHandler):

    def get(self):
        providerkey = self.request.get('providerkey')
        servicekey = self.request.get('servicekey')
        service = Service.get(servicekey)
        if service:
            #recursive delete
            service.rdelete()

        self.redirect('/services/provider/viewprovider?providerkey=%s' % providerkey)

