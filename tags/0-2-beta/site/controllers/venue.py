import os
import logging
import urllib
from datetime import datetime, timedelta
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.runtime import DeadlineExceededError
from google.appengine.ext.db import djangoforms
from google.appengine.api.labs.taskqueue import Task
from django import newforms as forms

from controllers.home import BASE_PATH, PROJECT_PATH
from models.bookinginfo import ContractedBooking
from models.hostinfo import Owner, Venue
from models.codelookup import getChoicesTuple
from controllers.utils import get_authentication_urls

logger = logging.getLogger('VenueHandler')


class VenueForm(djangoforms.ModelForm):
    class Meta:
        model = Venue
        exclude = ['owner', 'created', 'creator', 'state', 'numberOfBookings']

    venueType = forms.ChoiceField(choices=getChoicesTuple(('ACTYP')))

class ViewVenue(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'viewvenue.html')
        if self.request.get('limited_view'):
            limited_view = self.request.get('limited_view', 'True') == 'True'
            expiration = datetime.now() + timedelta(days=30)
            self.response.headers.add_header(
                'Set-Cookie',
                'limited_view=%s expires=%s' \
                    % (limited_view, expiration))
        else:
            limited_view = self.request.cookies.get('limited_view') == 'True'
        
        venuekey = self.request.get('venuekey')
        venue = Venue.get(venuekey)
        form = VenueForm(instance=venue)
        venue_values = []
        for field in form.fields.keyOrder:
            for value in venue.properties().values():
                if value.name == field:
                    name = value.name
                    if value.verbose_name:
                        name = value.verbose_name
                    val = value.get_value_for_form(venue)
                    venue_values.append((name, val))
        context = {}
        if not limited_view:
            photographs = venue.venue_photos
            inspections = venue.venue_inspections
            complaints = venue.venue_complaints
            bathrooms = venue.venue_bathrooms
            contractedbookings = \
              [ContractedBooking.get(k) for k in venue.getContractedBookings()]
            context = {
                'photographs':photographs,
                'inspections':inspections,
                'complaints':complaints,
                'bathrooms':bathrooms,
                'contractedbookings':contractedbookings,
                }

        addresses = venue.entity_addresses
        phonenumbers = venue.entity_phonenumbers
        bedrooms = venue.venue_bedrooms.order('name')
        emails = venue.entity_emails
        ownerkey = venue.owner.key()
        context['addresses'] = addresses
        context['limited_view'] = limited_view
        context['base_path'] = BASE_PATH
        context['ownerkey'] = ownerkey
        context['owner_name'] = venue.owner.listing_name()
        context['venue'] = venue
        context['venue_values'] = venue_values
        context['phonenumbers'] = phonenumbers
        context['bedrooms'] = bedrooms
        context['emails'] = emails
        context['user'] = users.get_current_user()
        context['is_admin_user'] = users.is_current_user_admin()
        context['auth_url'] = auth_url
        context['auth_url_text'] = auth_url_text

        self.response.out.write(template.render(filepath, context))

    def post(self):
        venuekey = self.request.get('venuekey')
        venue = Venue.get(venuekey)
        state = self.request.get('state')
        workflow = self.request.get('workflow')
        validate_venue = self.request.get('validate_venue')
        validate_slots = self.request.get('validate_slots')
        clear_slots = self.request.get('clear')
        create_slots = self.request.get('create')
        if clear_slots:
            try:
                venue.deleteAllSlots()
            except DeadlineExceededError:
                self.response.clear()
                self.response.set_status(500)
                self.response.out.write(
                    "Operation took too long, please try again")
                params = {}
                params['error'] = 'Operation timed out'
                params['came_from'] = self.request.referer
                params = urllib.urlencode(params)
                url = '/home/showerror?%s' % params
                self.redirect(url)
        if create_slots:
            params = {}
            params['came_from'] = self.request.referer
            try:
                numCreated = venue.createSlots()
                if numCreated == 0:
                    params['error'] = 'All slots have been created'
                else:
                    params['error'] = 'Created %s slots' % numCreated
            except DeadlineExceededError:
                self.response.clear()
                self.response.set_status(500)
                self.response.out.write(
                    "Operation took too long, please try again")
                params['error'] = 'Operation timed out'
            params = urllib.urlencode(params)
            url = '/home/showerror?%s' % params
            self.redirect(url)
            return
        if validate_slots:
            is_valid, err = venue.validate()
            params = {}
            numNights, numSlots = venue.validateSlots()
            if numNights == numSlots:
                params['error'] = 'Slots are valid'
            else:
                params['error'] = \
                  "Of the total of %s contracted nights, %s slots exist" % (
                      numNights, numSlots)
            params['came_from'] = self.request.referer
            params = urllib.urlencode(params)
            url = '/home/showerror?%s' % params
            self.redirect(url)
            return
        if validate_venue:
            is_valid, err = venue.validate()
            params = {}
            if is_valid:
                params['error'] = 'Venue is valid'
            else:
                params['error'] = err
            params['came_from'] = self.request.referer
            params = urllib.urlencode(params)
            url = '/home/showerror?%s' % params
            self.redirect(url)
            return
        if workflow:
            if state == 'Closed':
                #Validate first
                is_valid, err = venue.validate()
                if not is_valid:
                    params = {}
                    params['came_from'] = self.request.referer
                    params['error'] = err
                    params = urllib.urlencode(params)
                    url = '/home/showerror?%s' % params
                    self.redirect(url)
                    return

                venue.state = 'Open'
                venue.put()
                logger.info('Opened venue %s', 
                    "%s %s" % (venue.owner.referenceNumber, venue.name))
                task = Task(
                    method='GET',
                    url='/tasks/createslots',
                    params={'venuekey': venue.key()})
                task.add('slot-creation')
            elif state == 'Open':
                venue.state = 'Closed'
                venue.put()
        self.redirect('/services/owner/viewvenue?venuekey=%s' % venuekey)

class CaptureVenue(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                                  'templates', 'services', 'capturevenue.html')
        ownerkey = self.request.get('ownerkey')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':VenueForm(),
                                        'ownerkey':ownerkey,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        data = VenueForm(data=self.request.POST)
        ownerkey = self.request.get('ownerkey')
        owner = Owner.get(ownerkey)
        if data.is_valid():
            entity = data.save(commit=False)
            entity.creator = users.get_current_user()
            entity.owner = owner
            entity._parent_key = ownerkey
            entity._parent = owner
            entity.put()
            self.redirect('/services/owner/viewowner?ownerkey=%s' % ownerkey)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'capturevenue.html')
            self.response.out.write(template.render(filepath, 
                      {'base_path':BASE_PATH,
                       'form':data,
                       'ownerkey':ownerkey,
                       'auth_url':auth_url,
                       'auth_url_text':auth_url_text
                                               }))


class EditVenue(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        venuekey = self.request.get('venuekey')
        venue = Venue.get(venuekey)
        ownerkey = self.request.get('ownerkey')
        filepath = os.path.join(PROJECT_PATH, 
                                    'templates', 'services', 'editvenue.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':VenueForm(instance=venue),
                                        'venuekey':venuekey,
                                        'ownerkey':ownerkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        venuekey = self.request.get('venuekey')
        venue = Venue.get(venuekey)
        ownerkey = self.request.get('ownerkey')
        data = VenueForm(data=self.request.POST, instance=venue)
        if data.is_valid():
            entity = data.save(commit=False)
            if not self.request.get('contractStartDate'):
                entity.contractStartDate = None
            if not self.request.get('contractEndDate'):
                entity.contractEndDate = None
            #Change creator to last modified
            entity.creator = users.get_current_user()
            entity._parent_key = ownerkey
            entity._parent = venue.owner
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                                        'templates', 'services', 'editvenue.html')
            self.response.out.write(template.render(filepath, 
                                        {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'venuekey':venuekey,
                                        'ownerkey':ownerkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class DeleteVenue(webapp.RequestHandler):

    def get(self):
        ownerkey = self.request.get('ownerkey')
        venuekey = self.request.get('venuekey')
        venue = Venue.get(venuekey)
        if venue:
            #recursive delete
            venue.rdelete()

        self.redirect('/services/owner/viewowner?ownerkey=%s' % ownerkey)

