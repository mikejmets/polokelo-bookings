import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.bookinginfo import BookingRequest
from controllers.utils import get_authentication_urls

logger = logging.getLogger('BookingRequestHandler')


class BookingRequestForm(djangoforms.ModelForm):
    class Meta:
        model = BookingRequest
        exclude = ['created', 'creator']


class CaptureBookingRequest(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'bookings', 'capturebookingrequest.html')
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'form':BookingRequestForm(),
                        'auth_url':auth_url,
                        'auth_url_text':auth_url_text
                        }))

    def post(self):
        data = BookingRequestForm(data=self.request.POST)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect('/bookings/bookinginfo')
        else:
            filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'bookings', 'capturebookingrequest.html')
            self.response.out.write(template.render(filepath, 
                        {'base_path':BASE_PATH,
                         'form':data
                         }))


class EditBookingRequest(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        bookingrequestkey = self.request.get('bookingrequestkey')
        bookingrequest = BookingRequest.get(bookingrequestkey)
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'bookings', 'editbookingrequest.html')
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'form':BookingRequestForm(instance=bookingrequest),
                        'bookingrequestkey':bookingrequestkey,
                        'auth_url':auth_url,
                        'auth_url_text':auth_url_text
                        }))

    def post(self):
        bookingrequestkey = self.request.get('bookingrequestkey')
        bookingrequest = BookingRequest.get(bookingrequestkey)
        data = BookingRequestForm(
                  data=self.request.POST, instance=bookingrequest)
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
                          'templates', 'bookings', 'editbookingrequest.html')
            self.response.out.write(template.render(filepath, 
                          {
                              'base_path':BASE_PATH,
                              'form':data,
                              'bookingrequestkey':bookingrequestkey
                              }))


class DeleteBookingRequest(webapp.RequestHandler):

    def get(self):
        bookingrequestkey = self.request.get('bookingrequestkey')
        bookingrequest = BookingRequest.get(bookingrequestkey)
        if bookingrequest:
            #recursive delete
            bookingrequest.rdelete()

        self.redirect('/bookings/bookinginfo')

