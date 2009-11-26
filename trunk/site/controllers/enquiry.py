import os
import urllib
import logging
from datetime import datetime
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext import db

from controllers.bookingstool import BookingsTool
from controllers.home import BASE_PATH, PROJECT_PATH
from models.hostinfo import Berth
from models.bookinginfo import Enquiry, EnquiryCollection, \
    ContractedBooking, AccommodationElement
from controllers.utils import get_authentication_urls
from controllers import generator
from workflow.__init__ import ENQUIRY_WORKFLOW
from models.codelookup import getChoices

logger = logging.getLogger('EnquiryHandler')


class EnquiryForm(djangoforms.ModelForm):
    class Meta:
        model = Enquiry
        exclude = ['created', 'creator', 'workflow', 'referenceNumber',
            'workflowState', 'enqColl', 'xmlSource']


class ViewEnquiry(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'bookings', 'viewenquiry.html')
        enquirykey = self.request.get('enquirykey')
        enquiry = Enquiry.get(enquirykey)
        element = AccommodationElement.all().ancestor(enquiry)[0]
        show_search = enquiry.workflowState in \
            ['temporary', 'requiresintervention']
        show_transitions = enquiry.workflowState not in \
            ['temporary', 'requiresintervention', 'expired', 'cancelled']
        transitions = None
        if show_transitions:
            transitions = enquiry.getPossibleTransitions()
        cities = getChoices('CTY')
        accommodationTypes = getChoices('ACTYP')
        berths = []
        show_results = show_search
        if show_results:
            if element.availableBerths:
                for key, slots in eval(element.availableBerths):
                    berth = Berth.get(key)
                    berths.append(berth)
            if berths:
                #sort
                berths.sort(key=lambda x: "%s %s %s %s" % (
                    x.bed.bedroom.venue.owner.listing_name(),
                    x.bed.bedroom.venue.name,
                    x.bed.bedroom.name,
                    x.bed.name))
            else:
                show_results = False
        show_bookings = len(enquiry.contracted_bookings.fetch(1)) > 0
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'enquiry': enquiry,
                        'element': element,
                        'show_search':show_search,
                        'show_transitions':show_transitions,
                        'show_results':show_results,
                        'show_bookings':show_bookings,
                        'transitions':transitions,
                        'cities':cities,
                        'accomtypes':accommodationTypes,
                        'berths':berths,
                        'auth_url':auth_url,
                        'auth_url_text':auth_url_text,
                        }))


class AdvanceEnquiry(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'bookings', 'viewenquiry.html')
        enquirykey = self.request.get('enquirykey')
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'enquirykey': enquirykey,
                        'auth_url':auth_url,
                        'auth_url_text':auth_url_text
                        }))


    def post(self):
        enquirykey = self.request.get('enquirykey')
        enquiry = Enquiry.get(enquirykey)
        transition = self.request.get('transition')
        enquiry.doTransition(transition)

        params = {}
        params['enquirykey'] = enquirykey
        params = urllib.urlencode(params)
        self.redirect('/bookings/enquiry/viewenquiry?%s' % params)

class CaptureEnquiry(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        enquirycollectionkey = self.request.get('enquirycollectionkey')
        collection = EnquiryCollection.get(enquirycollectionkey)
        enquiry = Enquiry(
            parent=collection,
            referenceNumber=generator.generateEnquiryNumber())
        enquiry.put()
        enquiry.enterWorkflow(ENQUIRY_WORKFLOW)
        accom_element = AccommodationElement(parent=enquiry)
        accom_element.put()
        self.redirect('/bookings/enquiry/viewenquiry?enquirykey=%s' % enquiry.key())


class EditEnquiry(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        came_from = self.request.referer
        enquirykey = self.request.get('enquirykey')
        enquiry = Enquiry.get(enquirykey)
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'bookings', 'editenquiry.html')
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'form':EnquiryForm(instance=enquiry),
                        'enquirykey':enquirykey,
                        'came_from':came_from,
                        'enquirykey':enquirykey,
                        'auth_url':auth_url,
                        'auth_url_text':auth_url_text
                        }))

    def post(self):
        enquirykey = self.request.get('enquirykey')
        enquiry = Enquiry.get(enquirykey)
        came_from = self.request.get('came_from')
        data = EnquiryForm(
                  data=self.request.POST, instance=enquiry)
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
                          'templates', 'bookings', 'editenquiry.html')
            self.response.out.write(template.render(filepath, 
                          {
                              'base_path':BASE_PATH,
                              'form':data,
                              'came_from':came_from,
                              'enquirykey':enquirykey
                              }))


class DeleteEnquiry(webapp.RequestHandler):

    def get(self):
        enquirykey = self.request.get('enquirykey')
        enquiry = Enquiry.get(enquirykey)
        collectionkey = enquiry.parent().key()
        if enquiry:
            #recursive delete
            enquiry.rdelete()

        self.redirect('/bookings/collection/viewenquirycollection?enquirycollectionkey=%s' % collectionkey)

class BookingsToolFindAccommodation(webapp.RequestHandler):

    def post(self):
        enquirykey = self.request.get('enquirykey')
        enquiry = Enquiry.get(enquirykey)
        accom_element = AccommodationElement.all().ancestor(enquiry)[0]
        accom_element.city = self.request.get('city')
        accom_element.type = self.request.get('type')
        accom_element.start = datetime.strptime(
            self.request.get('start'),
            '%Y-%m-%d').date()
        accom_element.nights = int(self.request.get('nights', '0'))
        accom_element.adults = int(self.request.get('adults', '0'))
        accom_element.children = int(self.request.get('children', '0'))
        accom_element.children = int(self.request.get('children', '0'))
        accom_element.children = int(self.request.get('children', '0'))
        accom_element.doublerooms = int(self.request.get('doublerooms', '0'))
        accom_element.singlerooms = int(self.request.get('singlerooms', '0'))
        accom_element.put()

        tool = BookingsTool()
        berths = tool.findBerths(accom_element)

        params = {}
        params['enquirykey'] = enquirykey
        if berths:
            accom_element.availableBerths = str(berths)
            accom_element.put()
            params = urllib.urlencode(params)
            self.redirect('/bookings/enquiry/viewenquiry?%s' % params)
        else:
            #Clean up
            accom_element.availableBerths = None
            accom_element.put()
            if enquiry.workflowState != 'requiresintervention':
                enquiry.doTransition('assigntouser')
            params['error'] = "No results found" 
            params = urllib.urlencode(params)
            self.redirect('/bookings/bookingerror?%s' % params)

class BookingsToolReserveAccommodation(webapp.RequestHandler):
    def post(self):
        args = self.request.arguments()
        enquirykey =  self.request.get('enquirykey')
        enquiry = Enquiry.get(enquirykey)
        element = AccommodationElement.all().ancestor(enquiry)[0]
        error = None
        if element.availableBerths:
            berthkeys = []
            for arg in args:
                if arg.startswith('berth_'):
                    berthkey = arg[6:]
                    berthkeys.append(berthkey)
            if berthkeys:
                tool = BookingsTool()
                error = tool.createBookings(enquiry, element, berthkeys)
            else:
                error = "No berths selected"

        element.availableBerths = None
        element.put()
        params = {}
        params['enquirykey'] =  enquirykey
        if error:
            #Clean up
            params['error'] = error 
            params = urllib.urlencode(params)
            self.redirect('/bookings/bookingerror?%s' % params)
        else:
            params = urllib.urlencode(params)
            self.redirect('/bookings/enquiry/viewenquiry?%s' % params)

