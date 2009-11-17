import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.bookinginfo import Enquiry
from controllers.utils import get_authentication_urls

logger = logging.getLogger('EnquiryHandler')


class EnquiryForm(djangoforms.ModelForm):
    class Meta:
        model = Enquiry
        exclude = ['created', 'creator']


class CaptureEnquiry(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'bookings', 'captureenquiry.html')
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'form':EnquiryForm(),
                        'auth_url':auth_url,
                        'auth_url_text':auth_url_text
                        }))

    def post(self):
        data = EnquiryForm(data=self.request.POST)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect('/bookings/bookinginfo')
        else:
            filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'bookings', 'captureenquiry.html')
            self.response.out.write(template.render(filepath, 
                        {'base_path':BASE_PATH,
                         'form':data
                         }))


class EditEnquiry(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        enquirykey = self.request.get('enquirykey')
        enquiry = Enquiry.get(enquirykey)
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'bookings', 'editenquiry.html')
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'form':EnquiryForm(instance=enquiry),
                        'enquirykey':enquirykey,
                        'auth_url':auth_url,
                        'auth_url_text':auth_url_text
                        }))

    def post(self):
        enquirykey = self.request.get('enquirykey')
        enquiry = Enquiry.get(enquirykey)
        data = EnquiryForm(
                  data=self.request.POST, instance=enquiry)
        if data.is_valid():
            entity = data.save(commit=False)
            #Extra work for non required date fields
            if not self.request.get('startDate'):
                entity.startDate = None
            #Change creator to last modified
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect('/bookings/bookinginfo')
        else:
            filepath = os.path.join(PROJECT_PATH, 
                          'templates', 'bookings', 'editenquiry.html')
            self.response.out.write(template.render(filepath, 
                          {
                              'base_path':BASE_PATH,
                              'form':data,
                              'enquirykey':enquirykey
                              }))


class DeleteEnquiry(webapp.RequestHandler):

    def get(self):
        enquirykey = self.request.get('enquirykey')
        enquiry = Enquiry.get(enquirykey)
        if enquiry:
            #recursive delete
            enquiry.rdelete()

        self.redirect('/bookings/bookinginfo')

