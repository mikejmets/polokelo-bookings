import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.bookinginfo import ContractedBooking
from controllers.utils import get_authentication_urls

logger = logging.getLogger('ContractedBookingHandler')


class ContractedBookingForm(djangoforms.ModelForm):
    class Meta:
        model = ContractedBooking
        exclude = ['created', 'creator', 'client', 'enquiry']


class CaptureContractedBooking(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'bookings', 'capturecontractedbooking.html')
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'form':ContractedBookingForm(),
                        'auth_url':auth_url,
                        'auth_url_text':auth_url_text
                        }))

    def post(self):
        data = ContractedBookingForm(data=self.request.POST)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect('/bookings/bookinginfo')
        else:
            filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'bookings', 'capturecontractedbooking.html')
            self.response.out.write(template.render(filepath, 
                        {'base_path':BASE_PATH,
                         'form':data
                         }))


class EditContractedBooking(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        contractedbookingkey = self.request.get('contractedbookingkey')
        contractedbooking = ContractedBooking.get(contractedbookingkey)
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'bookings', 'editcontractedbooking.html')
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'form':ContractedBookingForm(instance=contractedbooking),
                        'contractedbookingkey':contractedbookingkey,
                        'auth_url':auth_url,
                        'auth_url_text':auth_url_text
                        }))

    def post(self):
        contractedbookingkey = self.request.get('contractedbookingkey')
        contractedbooking = ContractedBooking.get(contractedbookingkey)
        data = ContractedBookingForm(
                  data=self.request.POST, instance=contractedbooking)
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
                          'templates', 'bookings', 'editcontractedbooking.html')
            self.response.out.write(template.render(filepath, 
                          {
                              'base_path':BASE_PATH,
                              'form':data,
                              'contractedbookingkey':contractedbookingkey
                              }))


class DeleteContractedBooking(webapp.RequestHandler):

    def get(self):
        contractedbookingkey = self.request.get('contractedbookingkey')
        contractedbooking = ContractedBooking.get(contractedbookingkey)
        if contractedbooking:
            #recursive delete
            contractedbooking.rdelete()

        self.redirect('/bookings/bookinginfo')

