import os
import logging
from google.appengine.api import users, images
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext import db
from google.appengine.runtime.apiproxy_errors import RequestTooLargeError

from controllers.home import BASE_PATH, PROJECT_PATH
from models.hostinfo import Photograph, Venue
from controllers.utils import get_authentication_urls

logger = logging.getLogger('PhotographHandler')


class CapturePhotograph(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        venuekey = self.request.get('venuekey')
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'capturephotograph.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'venuekey':venuekey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        venuekey = self.request.get('venuekey')
        venue = Venue.get(venuekey)
        caption = self.request.get('caption')
        caption = caption.strip()
        try:
            if caption:
                photo = Photograph.get_or_insert(caption)
                photo.creator = users.get_current_user()
                photo.venue = venue
                photo._parent_key = venuekey
                photo._parent = venue
                photo.caption = caption
                rawphoto = self.request.get('fullsize')
                photo.thumbnail = db.Blob(images.resize(rawphoto, 132, 132))
                photo.fullsize = db.Blob(images.resize(rawphoto, 640, 640))
                photo.put()

            self.redirect(came_from)

        except RequestTooLargeError:
            error_message = "The image file size you are trying to upload is over 1MB." +                             " Please resize the image so that the file size is below 1MB"
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'capturephotograph.html')
            self.response.out.write(template.render(filepath, 
                                        {
                                            'base_path':BASE_PATH,
                                            'venuekey':venuekey,
                                            'came_from':came_from,
                                            'auth_url':auth_url,
                                            'auth_url_text':auth_url_text,
                                            'caption':caption,
                                            'error_msg':error_message
                                            }))

class EditPhotograph(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        photokey = self.request.get('photokey')
        photo = Photograph.get(photokey)
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'editphotograph.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'photo':photo,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        photokey = self.request.get('photokey')
        photo = Photograph.get(photokey)
        caption = self.request.get('caption')
        caption = caption.strip()
        try:
            if caption:
                photo = Photograph.get(photokey)
                photo.creator = users.get_current_user()
                photo.caption = caption
                # rawphoto = self.request.get('fullsize')
                # photo.thumbnail = db.Blob(images.resize(rawphoto, 132, 132))
                # photo.fullsize = db.Blob(images.resize(rawphoto, 640, 640))
                photo._parent_key = photo.venue.key()
                photo._parent = photo.venue
                photo.put()

            self.redirect(came_from)

        except RequestTooLargeError:
            error_message = "The image file size you are trying to upload is over 1MB." +                             " Please resize the image so that the file size is below 1MB"
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'editphotograph.html')
            self.response.out.write(template.render(filepath, 
                                        {
                                            'base_path':BASE_PATH,
                                            'photo':photo,
                                            'came_from':came_from,
                                            'auth_url':auth_url,
                                            'auth_url_text':auth_url_text,
                                            'error_msg':error_message
                                            }))


class DeletePhotograph(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        key = self.request.get('photokey')
        photo = Photograph.get(key)
        if photo:
            photo.delete()
        self.redirect(came_from)


