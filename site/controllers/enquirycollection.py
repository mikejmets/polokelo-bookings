import os
import urllib
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.bookinginfo import EnquiryCollection, Enquiry
from controllers.utils import get_authentication_urls
from controllers import generator

logger = logging.getLogger('EnquiryCollectionHandler')


class EnquiryCollectionForm(djangoforms.ModelForm):
    class Meta:
        model = EnquiryCollection
        exclude = ['created', 'creator']


class ViewEnquiryCollection(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'bookings', 'viewenquirycollection.html')
        enquirycollectionkey = self.request.get('enquirycollectionkey')
        logger.info('---------%s', enquirycollectionkey)
        enquirycollection = EnquiryCollection.get(enquirycollectionkey)
        enquiries = Enquiry.all().ancestor(enquirycollection)
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'enquirycollectionkey': enquirycollectionkey,
                        'enquirycollection': enquirycollection,
                        'enquiries':enquiries,
                        'auth_url':auth_url,
                        'auth_url_text':auth_url_text
                        }))

    def post(self):
        transition = self.request.get('transition')
        enquirycollectionkey = self.request.get('enquirycollectionkey') 
        enquirycollection = EnquiryCollection.get(enquirycollectionkey)
        params = {}
        params['enquirycollectionkey'] = enquirycollectionkey 
        params = urllib.urlencode(params)
        self.redirect('/bookings/enquiry/viewenquirycollection?%s' % params)

class CaptureEnquiryCollection(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        collection = EnquiryCollection(
            referenceNumber=generator.generateEnquiryCollectionNumber())
        collection.put()
        self.redirect('/bookings/collection/viewenquirycollection?enquirycollectionkey=%s' % collection.key())



class EditEnquiryCollection(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        came_from = self.request.referer
        enquirycollectionkey = self.request.get('enquirycollectionkey')
        enquirycollection = EnquiryCollection.get(enquirycollectionkey)
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'bookings', 'editenquirycollection.html')
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'form':EnquiryCollectionForm(instance=enquirycollection),
                        'enquirycollectionkey':enquirycollectionkey,
                        'came_from':came_from,
                        'enquirycollectionkey':enquirycollectionkey,
                        'auth_url':auth_url,
                        'auth_url_text':auth_url_text
                        }))

    def post(self):
        enquirycollectionkey = self.request.get('enquirycollectionkey')
        enquirycollection = EnquiryCollection.get(enquirycollectionkey)
        came_from = self.request.get('came_from')
        data = EnquiryCollectionForm(
                  data=self.request.POST, instance=enquirycollection)
        if data.is_valid():
            entity = data.save(commit=False)
            #Extra work for non required date fields
            if not self.request.get('startDate'):
                entity.startDate = None
            #Change creator to last modified
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect(came_from)
        else:
            filepath = os.path.join(PROJECT_PATH, 
                          'templates', 'bookings', 'editenquirycollection.html')
            self.response.out.write(template.render(filepath, 
                          {
                              'base_path':BASE_PATH,
                              'form':data,
                              'came_from':came_from,
                              'enquirycollectionkey':enquirycollectionkey
                              }))


class DeleteEnquiryCollection(webapp.RequestHandler):

    def get(self):
        enquirycollectionkey = self.request.get('enquirycollectionkey')
        enquirycollection = EnquiryCollection.get(enquirycollectionkey)
        if enquirycollection:
            #recursive delete
            enquirycollection.rdelete()

        self.redirect('/bookings/bookinginfo')

