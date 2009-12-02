import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from django import newforms as forms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.bookinginfo import ContractedBooking
from models.clientinfo import Client
from models.codelookup import getChoicesTuple
from controllers.utils import get_authentication_urls
from controllers import generator

logger = logging.getLogger('ContractedBookingHandler')


class ContractedBookingForm(djangoforms.ModelForm):
    class Meta:
        model = ContractedBooking
        exclude = ['created', 'creator', 'client', 'enquiry', 'bookingNumber']

    state = forms.ChoiceField(choices=getChoicesTuple(('CBSTA')))

class ViewContractedBooking(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        bookingkey = self.request.get('bookingkey')
        booking = ContractedBooking.get(bookingkey)
        client = booking.client

        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'bookings', 'viewcontractedbooking.html')
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'booking':booking,
                        'client':client,
                        'auth_url':auth_url,
                        'auth_url_text':auth_url_text
                        }))

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
            entity.bookingNumber(generator.generateBookingNumber())
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

class AssignClientToBooking(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        came_from = self.request.get('came_from')
        bookingkey = self.request.get('bookingkey')
        booking = ContractedBooking.get(bookingkey)
        clientkey = self.request.get('clientkey', None)
        if not clientkey and booking.client:
            clientkey = booking.client.key()
        clientlist = []
        for client in Client.all():
            clientlist.append(
                (str(client.key()), "%s %s" % (client.surname, client.firstNames)))
        clientlist.insert(0, (None, '-----'))

        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'bookings', 'assignclient.html')
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'booking':booking,
                        'clientkey':clientkey,
                        'clientlist':clientlist,
                        'came_from':came_from,
                        'auth_url':auth_url,
                        'auth_url_text':auth_url_text
                        }))

    def post(self):
        bookingkey = self.request.get('bookingkey')
        booking = ContractedBooking.get(bookingkey)
        clientkey = self.request.get('clientkey')
        if clientkey:
            client = Client.get(clientkey)
            booking.client = client
            booking.put()
            self.redirect(
                '/bookings/viewcontractedbooking?bookingkey=%s' % bookingkey)
        else:
            filepath = os.path.join(PROJECT_PATH, 
                          'templates', 'bookings', 'assignclient.html')
            self.response.out.write(template.render(filepath, 
                          {
                              'base_path':BASE_PATH,
                              'bookingkey':bookingkey
                              }))
