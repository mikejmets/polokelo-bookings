import os
import urllib
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.enquiryroot import EnquiryRoot
from models.bookinginfo import EnquiryCollection, Enquiry, GuestElement
from controllers.utils import get_authentication_urls
from controllers import generator


class ViewGuestElement(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'guestelement', 'viewguestelement.html')
        guestkey = self.request.get('guestkey')
        guest = GuestElement.get(guestkey)
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'came_from':came_from,
                        'guestelement':guest,
                        'auth_url':auth_url,
                        'auth_url_text':auth_url_text
                        }))


class GuestElementForm(djangoforms.ModelForm):
    class Meta:
        model = GuestElement
        exclude = ['created', 'creator', 'isPrimary', 'enquiries', 'xmlSource']


class CaptureGuestElement(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        coll_key = self.request.get('coll_key')
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'guestelement', 'captureguestelement.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'coll_key':coll_key,
                                        'form':GuestElementForm(),
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        coll_key = self.request.get('coll_key')
        theparent = EnquiryCollection.get(coll_key)
        data = GuestElementForm(data=self.request.POST)
        valid = data.is_valid()
        if valid:
            guest = GuestElement(parent=theparent).all().filter('isPrimary =', True).get()
            if guest:
                guest.rdelete()
            clean_data = data._cleaned_data()
            guest = GuestElement(parent=theparent,
                                surname=clean_data.get('surname'),
                                firstNames=clean_data.get('firstNames'))
            guest.creator = users.get_current_user()
            guest.isPrimary = True
            guest.email = clean_data.get('email')
            guest.contactNumber = clean_data.get('contactNumber')
            guest.identifyingNumber = clean_data.get('identifyingNumber')
            guest.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                          'templates', 'guestelement', 'captureguestelement.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'coll_key':coll_key,
                                        'form':data,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class EditGuestElement(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        guestkey = self.request.get('guestkey')
        card_holder = GuestElement.get(guestkey)
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'guestelement', 'editguestelement.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':GuestElementForm(instance=card_holder),
                                        'guestkey':guestkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        guestkey = self.request.get('guestkey')
        card_holder = GuestElement.get(guestkey)
        data = GuestElementForm(data=self.request.POST, instance=card_holder)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.isPrimary=True
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                          'templates', 'guestelement', 'editguestelement.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'guestkey':guestkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))
