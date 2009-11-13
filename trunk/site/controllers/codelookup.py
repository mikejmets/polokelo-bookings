import os
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms

from controllers.home import BASE_PATH, PROJECT_PATH
from models.codelookup import CodeLookup
from controllers.utils import get_authentication_urls


class LookupTablesRoot(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        lookuptables = CodeLookup.all().filter('container =', 'root')
        filepath = os.path.join(PROJECT_PATH, 'templates', 'admin', 'lookuptables.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'lookuptables':lookuptables,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class LookupTableForm(djangoforms.ModelForm):
    class Meta:
        model = CodeLookup
        exclude = ['created', 'creator', 'container', 'sort_order']

class CaptureLookupTable(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'admin', 'capturelookuptable.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':LookupTableForm(),
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        data = LookupTableForm(data=self.request.POST)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.container = 'root'
            entity.sort_order = -1
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                          'templates', 'admin', 'capturelookuptable.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

class EditLookupTable(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        lookupkey = self.request.get('lookupkey')
        lookup = CodeLookup.get(lookupkey)
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'admin', 'editlookuptable.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':LookupTableForm(instance=lookup),
                                        'lookupkey':lookupkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        lookupkey = self.request.get('lookupkey')
        lookup = CodeLookup.get(lookupkey)
        data = LookupTableForm(data=self.request.POST, instance=lookup)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                          'templates', 'admin', 'editlookuptable.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'lookupkey':lookupkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

class DeleteLookupTable(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        key = self.request.get('lookupkey')
        item = CodeLookup.get(key)
        if item:
            #recursive delete
            item.rdelete()
        self.redirect(came_from)


class ViewLookupTable(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        lookupkey = self.request.get('lookupkey')
        lookuptable = CodeLookup.get(lookupkey)
        shortcode = lookuptable.shortcode
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'admin', 'viewlookuptable.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'lookuptable':lookuptable,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))



class LookupItemForm(djangoforms.ModelForm):
    class Meta:
        model = CodeLookup
        exclude = ['created', 'creator', 'container']

class CaptureLookupItem(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        container_code = self.request.get('container_code')
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'admin', 'capturelookupitem.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':LookupItemForm(),
                                        'came_from':came_from,
                                        'container_code':container_code, 
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        container_code = self.request.get('container_code')
        data = LookupItemForm(data=self.request.POST)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.container = container_code
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                          'templates', 'admin', 'capturelookupitem.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'came_from':came_from,
                                        'container_code':container_code, 
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

class EditLookupItem(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        itemkey = self.request.get('itemkey')
        item = CodeLookup.get(itemkey)
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'admin', 'editlookupitem.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':LookupItemForm(instance=item),
                                        'itemkey':itemkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        itemkey = self.request.get('itemkey')
        item = CodeLookup.get(itemkey)
        data = LookupItemForm(data=self.request.POST, instance=item)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                          'templates', 'admin', 'editlookupitem.html')
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

class DeleteLookupItem(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        key = self.request.get('itemkey')
        item = CodeLookup.get(key)
        if item:
            #recursive delete
            item.rdelete()
        self.redirect(came_from)

