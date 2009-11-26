import os
from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms

from controllers.home import BASE_PATH, PROJECT_PATH
from models.packages import Package
from controllers.utils import get_authentication_urls


class PackageRoot(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        packages = Package.all()
        packages.order('city').order('basePriceInZAR').order('accommodationType')
        filepath = os.path.join(PROJECT_PATH, 'templates', 'admin', 'packages.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'packages':packages,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class PackageForm(djangoforms.ModelForm):
    class Meta:
        model = Package
        exclude = ['created', 'creator']

class CapturePackage(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'admin', 'capturepackage.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':PackageForm(),
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        data = PackageForm(data=self.request.POST)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                          'templates', 'admin', 'capturepackage.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class EditPackage(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        packagekey = self.request.get('packagekey')
        package = Package.get(packagekey)
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'admin', 'editpackage.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':PackageForm(instance=package),
                                        'packagekey':packagekey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        packagekey = self.request.get('packagekey')
        package = Package.get(packagekey)
        data = PackageForm(data=self.request.POST, instance=package)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                          'templates', 'admin', 'editpackage.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'packagekey':packagekey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class DeletePackage(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        key = self.request.get('packagekey')
        item = Package.get(key)
        if item:
            item.delete()
        self.redirect(came_from)


