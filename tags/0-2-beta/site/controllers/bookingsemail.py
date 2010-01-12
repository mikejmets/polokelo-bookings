import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from django import newforms as forms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.bookinginfo import Enquiry, AccommodationElement
from models.bookingsemail import BookingsEmail
from controllers.emailtool import EmailTool
from controllers.utils import get_authentication_urls

logger = logging.getLogger('BookingsEmailHandler')


class BookingsEmailForm(djangoforms.ModelForm):
    class Meta:
        model = BookingsEmail
        exclude = ['created', 'creator', 'action', 'status']


class CaptureBookingsEmail(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        enquirykey = self.request.get('enquirykey')
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'bookings', 'captureemail.html')
        self.response.out.write(template.render(filepath, 
                  {
                      'base_path':BASE_PATH,
                      'form':BookingsEmailForm(),
                      'enquirykey':enquirykey,
                      'came_from':came_from,
                      'post_url':self.request.uri,
                      'auth_url':auth_url,
                      'auth_url_text':auth_url_text
                      }))

    def post(self):
        submit = self.request.get('submit')
        came_from = self.request.get('came_from')
        if submit == 'Cancel':
            self.redirect(came_from)

        data = BookingsEmailForm(data=self.request.POST)
        enquirykey = self.request.get('enquirykey')
        enquiry = Enquiry.get(enquirykey)
        if data.is_valid():
            email = data.save(commit=False)
            email.creator = users.get_current_user()
            email._parent_key = enquirykey
            email._parent = enquiry
            email.put()
            if submit == 'Send Email':
                tool = EmailTool()
                element = AccommodationElement.all().ancestor(enquiry).fetch(1)
                email.status = tool.sendEmail(email, element[0])
                email.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'bookings', 'captureemail.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'enquirykey':enquirykey,
                                        'came_from':came_from,
                                        'post_url':self.request.uri,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

class EditBookingsEmail(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        emailkey = self.request.get('emailkey')
        email = BookingsEmail.get(emailkey)
        enquiry = email.parent()
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'bookings', 'editemail.html')
        self.response.out.write(template.render(filepath, 
                  {
                      'base_path':BASE_PATH,
                      'form':BookingsEmailForm(instance=email),
                      'emailkey':emailkey,
                      'enquirykey': enquiry.key,
                      'came_from':came_from,
                      'post_url':self.request.uri,
                      'auth_url':auth_url,
                      'auth_url_text':auth_url_text
                      }))

    def post(self):
        came_from = self.request.get('came_from')
        submit = self.request.get('submit')
        if submit == 'Cancel':
            self.redirect(came_from)

        emailkey = self.request.get('emailkey')
        email = BookingsEmail.get(emailkey)
        enquiry = email.parent()
        data = BookingsEmailForm(data=self.request.POST, instance=email)
        if data.is_valid():
            email = data.save(commit=False)
            email.creator = users.get_current_user()
            email.put()
            if submit == 'Re-send Email':
                tool = EmailTool()
                element = AccommodationElement.all().ancestor(enquiry).fetch(1)
                email.status = tool.sendEmail(email, element[0])
                email.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'bookings', 'editemail.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'emailkey':emailkey,
                                        'enquirykey':enquiry.key(),
                                        'came_from':came_from,
                                        'post_url':self.request.uri,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class DeleteBookingsEmail(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        key = self.request.get('emailkey')
        email = BookingsEmail.get(key)
        if email:
            #recursive delete
            email.rdelete()
        self.redirect(came_from)


