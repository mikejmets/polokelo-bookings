import os
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from django import newforms as forms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.hostinfo import Berth, Slot
from controllers.utils import get_authentication_urls
from models.codelookup import getChoicesTuple

logger = logging.getLogger('SlotHandler')


class SlotForm(djangoforms.ModelForm):
    class Meta:
        model = Slot
        exclude = ['created', 'creator']

class ViewSlot(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        slotkey = self.request.get('slotkey')
        slot = Slot.get(slotkey)
        berth = slot.berth
        form = SlotForm(instance=slot)
        slot_values = []
        for field in form.fields.keyOrder:
            for value in slot.properties().values():
                if value.name == field:
                    name = value.name
                    if value.verbose_name:
                        name = value.verbose_name
                    val = value.get_value_for_form(slot)
                    slot_values.append((name, val))
        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'services', 'viewslot.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':SlotForm(),
                                        'slot_values':slot_values,
                                        'berthkey':berth.key(),
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

