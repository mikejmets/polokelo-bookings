import os
import logging
import urllib
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.services import ServiceProvider, Service
from models.hostinfo import Address
from controllers.utils import get_authentication_urls
PAGESIZE = 15

logger = logging.getLogger('Provider')


class ProviderForm(djangoforms.ModelForm):

    class Meta:
        model = ServiceProvider
        exclude = ['created', 'creator']

class ManageProviders(webapp.RequestHandler):
    def get(self):

        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        start = self.request.get('start', ' ')
        new_start = start
        query = ServiceProvider.all().order('name')
        query.filter('name >=', start)
        providers = query.fetch(PAGESIZE+1)
        if providers:
            new_start = providers[-1].name

        filepath = os.path.join(
              PROJECT_PATH, 'templates', 'services', 'manageproviders.html')
        self.response.out.write(template.render(filepath, 
          {
              'base_path':BASE_PATH,
              'start':new_start,
              'providers':providers,
              'user':users.get_current_user(),
              'is_admin_user':users.is_current_user_admin(),
              'auth_url':auth_url,
              'auth_url_text':auth_url_text
              }))

class ViewProvider(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'services', 'viewprovider.html')
        providerkey = self.request.get('providerkey')
        provider = ServiceProvider.get(providerkey)
        form = ProviderForm(instance=provider)
        provider_values = []
        for field in form.fields.keyOrder:
            for value in provider.properties().values():
                if value.name == field:
                    name = value.name
                    if value.verbose_name:
                        name = value.verbose_name
                    val = value.get_value_for_form(provider)
                    provider_values.append((name, val))
        services = Service.all().ancestor(provider)
        addresses = provider.entity_addresses
        phonenumbers = provider.entity_phonenumbers
        emails = provider.entity_emails
        self.response.out.write(template.render(filepath, 
                {
                    'base_path':BASE_PATH,
                    'provider':provider,
                    'provider_values':provider_values,
                    'services':services,
                    'addresses':addresses,
                    'phonenumbers':phonenumbers,
                    'emails':emails,
                    'user':users.get_current_user(),
                    'is_admin_user':users.is_current_user_admin(),
                    'auth_url':auth_url,
                    'auth_url_text':auth_url_text
                    }))

    def post(self):
        providerkey = self.request.get('providerkey')
        provider = ServiceProvider.get(providerkey)
        servicekey = self.request.get('servicekey', None)
        params = {}
        if servicekey:
            service = Service.get(servicekey)
            action = self.request.get('action', None)
            if action == 'Open':
                is_valid, err = service.validate()
                if not is_valid:
                    params['error'] = err
                    params['came_from'] = \
                        '/services/provider/viewprovider?providerkey=%s' % providerkey
                    params = urllib.urlencode(params)
                    url = '/home/showerror?%s' % params
                    self.redirect(url)
                    return
                service.state = 'Open'
                service.put()
            elif action == 'Close':
                service.state = 'Closed'
                service.put()
            else:
                logging.error('Open Service on Provider receive incorrect action %s',
                    action)
        self.redirect('/services/provider/viewprovider?providerkey=%s' % providerkey)


class CaptureProvider(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                          'templates', 'services', 'captureprovider.html')
        self.response.out.write(template.render(filepath, 
                {
                    'base_path':BASE_PATH,
                    'form':ProviderForm(),
                    'user':users.get_current_user(),
                    'auth_url':auth_url,
                    'auth_url_text':auth_url_text
                    }))

    def post(self):
        data = ProviderForm(data=self.request.POST)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect('/services/providers')
        else:
            filepath = os.path.join(PROJECT_PATH, 
                          'templates', 'services', 'captureprovider.html')
            self.response.out.write(template.render(filepath, {'base_path':BASE_PATH,
                                                               'form':data
                                                               }))


class EditProvider(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        providerkey = self.request.get('providerkey')
        provider = ServiceProvider.get(providerkey)
        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'services', 'editprovider.html')
        self.response.out.write(template.render(filepath, 
                {
                    'base_path':BASE_PATH,
                    'form':ProviderForm(instance=provider),
                    'providerkey':providerkey,
                    'user':users.get_current_user(),
                    'auth_url':auth_url,
                    'auth_url_text':auth_url_text
                    }))

    def post(self):
        providerkey = self.request.get('providerkey')
        provider = ServiceProvider.get(providerkey)
        data = ProviderForm(data=self.request.POST, instance=provider)
        if data.is_valid():
            entity = data.save(commit=False)
            #Change creator to last modified
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect('/services/providers')
        else:
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'editprovider.html')
            self.response.out.write(template.render(filepath, 
                                        {
                                            'base_path':BASE_PATH,
                                            'form':data,
                                            'providerkey':providerkey
                                            }))


class DeleteProvider(webapp.RequestHandler):

    def get(self):
        providerkey = self.request.get('providerkey')
        provider = ServiceProvider.get(providerkey)
        if provider:
            #recursive delete
            provider.rdelete()

        self.redirect('/services/providers')

