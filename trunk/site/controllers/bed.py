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

logger = logging.getLogger('BedHandler')


class BedForm(djangoforms.ModelForm):
    class Meta:
        model = Bed
        exclude = ['created', 'creator', 'bedroom']

    bedType = forms.ChoiceField(choices=getChoicesTuple(('BEDTP')))

class ViewBed(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        bedkey = self.request.get('bedkey')
        bed = Bed.get(bedkey)
        form = BedForm(instance=bed)
        bed_values = []
        for field in form.fields.keyOrder:
            for value in bed.properties().values():
                if value.name == field:
                    name = value.name
                    if value.verbose_name:
                        name = value.verbose_name
                    val = value.get_value_for_form(bed)
                    bed_values.append((name, val))
        bed_values.append(('created', bed.created))
        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'services', 'viewbed.html')
        self.response.out.write(template.render(filepath, 
              {
                  'base_path':BASE_PATH,
                  'form':BedForm(),
                  'bed_values':bed_values,
                  'bedroomkey':bed.bedroom.key(),
                  'berths':bed.bed_berths,
                  'came_from':came_from,
                  'user':users.get_current_user(),
                  'auth_url':auth_url,
                  'auth_url_text':auth_url_text
                  }))

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
                    'user':users.get_current_user(),
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
            bed._parent_key = containerkey
            bed._parent = container
            bed.put()
            #auto create a berth per capacity
            bed.createBerths()
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
                    'user':users.get_current_user(),
                    'auth_url':auth_url,
                    'auth_url_text':auth_url_text
                    }))

    def post(self):
        came_from = self.request.get('came_from')
        bedkey = self.request.get('bedkey')
        bed = Bed.get(bedkey)
        container = bed.bedroom
        data = BedForm(data=self.request.POST)
        if data.is_valid():
            new_bed = data.save(commit=False)
            new_bed.creator = users.get_current_user()
            new_bed._parent_key = container.key()
            new_bed._parent = container
            new_bed.bedroom = container
            new_bed.put()
            bed.rdelete()
            #Auto delete and recreate all berths
            for i in new_bed.bed_berths:
                i.rdelete()
            for i in range(new_bed.capacity):
                berth = Berth(parent=new_bed)
                berth.creator = users.get_current_user()
                berth.bed = new_bed
                berth.put()
            self.redirect(came_from)
        else:
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


