import sys
import os
import urllib
import logging
from datetime import datetime
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext import db
from google.appengine.runtime import DeadlineExceededError

from controllers.bookingstool import BookingsTool
from controllers.home import BASE_PATH, PROJECT_PATH
from models.hostinfo import Berth
from models.enquiryroot import EnquiryRoot
from models.bookinginfo import Enquiry, EnquiryCollection, \
                                    AccommodationElement
from controllers.utils import get_authentication_urls
from controllers import generator
from models.packages import Package
from models.codelookup import getChoices
from workflow.workflow import WorkflowError

logger = logging.getLogger('EnquiryHandler')


class EnquiryForm(djangoforms.ModelForm):
    class Meta:
        model = Enquiry
        exclude = ['created', 'creator', 'workflow', 'referenceNumber',
            'workflowStateName', 'enqColl', 'xmlSource']


class ViewEnquiry(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'bookings', 'viewenquiry.html')
        enquirykey = self.request.get('enquirykey')
        enquiry = Enquiry.get(enquirykey)
        element = AccommodationElement.all().ancestor(enquiry)[0]
        show_search = enquiry.workflowStateName in \
            ['temporary', 'onhold', 'awaitingagent']
        show_transitions = enquiry.workflowStateName not in \
            ['temporary', 'onhold', 'awaitingagent', 'expired', 'cancelled']
        transitions = None
        if show_transitions:
            transitions = enquiry.getPossibleTransitions()
        cities = getChoices('CTY')
        accommodationTypes = getChoices('ACTYP')
        berths = []
        show_results = show_search
        if show_results:
            if element.availableBerths:
                venues = eval(element.availableBerths)
                for venue_key in venues:
                    for key, slots in venues[venue_key]:
                        berth = Berth.get(key)
                        berths.append(berth)
            if berths:
                #sort
                berths.sort(key=lambda b: "%s" % (
                    b.bed.bedroom.venue.fairAllocationsIndicator(b, element)))
            else:
                show_results = False
        show_bookings = len(enquiry.getContractedBookings()) > 0
        self.response.out.write(template.render(filepath, 
              {
                  'base_path':BASE_PATH,
                  'enquiry': enquiry,
                  'outstanding':'%0.2f' % ((enquiry.totalAmountInZAR - enquiry.amountPaidInZAR) / 100.0),
                  'element': element,
                  'show_search':show_search,
                  'show_transitions':show_transitions,
                  'show_results':show_results,
                  'show_bookings':show_bookings,
                  'transitions':transitions,
                  'cities':cities,
                  'accomtypes':accommodationTypes,
                  'berths':berths,
                  'user':users.get_current_user(),
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
                  'user':users.get_current_user(),
                  'auth_url':auth_url,
                  'auth_url_text':auth_url_text
                  }))


    def post(self):
        enquirykey = self.request.get('enquirykey')
        enquiry = Enquiry.get(enquirykey)
        transition = self.request.get('transition')
        error = None
        try:
            enquiry.doTransition(transition, txn_category='manual')
        except WorkflowError, e:
            error = e
        except:
            error = sys.exc_info()[1]

        params = {}
        params['enquirykey'] = enquirykey
        if error is None:
            params = urllib.urlencode(params)
            self.redirect('/bookings/enquiry/viewenquiry?%s' % params)
        else:
            params['error'] = error
            params = urllib.urlencode(params)
            self.redirect('/bookings/bookingerror?%s' % params)

class CaptureEnquiry(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        enquirycollectionkey = self.request.get('enquirycollectionkey')
        collection = EnquiryCollection.get(enquirycollectionkey)
        enquiry = Enquiry(
            parent=collection,
            referenceNumber=generator.generateEnquiryNumber())
        enquiry.put()
        enquiry.enterWorkflow(EnquiryRoot.getEnquiryWorkflow())
        accom_element = AccommodationElement(parent=enquiry)
        accom_element.put()
        enquiry.doTransition('temptoagent')
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
                  'user':users.get_current_user(),
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
                        'user':users.get_current_user(),
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
        accom_element.wheelchairAccess = \
            self.request.get('wheelchairAccess', 'off') != 'off'
        accom_element.adults = int(self.request.get('adults', '0'))
        accom_element.children = int(self.request.get('children', '0'))
        accom_element.doublerooms = int(self.request.get('doublerooms', '0'))
        accom_element.singlerooms = int(self.request.get('singlerooms', '0'))
        accom_element.put()

        # Check if we have a package for the accommodation type in the city.
        query = Package.all()
        query.filter('city =', accom_element.city)
        query.filter('accommodationType =', accom_element.type)
        package = query.get()

        if not package:
            #Clean up
            accom_element.availableBerths = None
            accom_element.put()
            if enquiry.workflowStateName not in \
                    ['onhold', 'awaitingagent', 'expired']:
                enquiry.doTransition('putonhold')

            params = {}
            params['enquirykey'] = enquirykey
            params['error'] = "No package found for %s in %s" % (
                accom_element.type,
                accom_element.city)
            params = urllib.urlencode(params)
            self.redirect('/bookings/bookingerror?%s' % params)
            return

        tool = BookingsTool()
        error = None
        try:
            venues = tool.findVenues(accom_element)
        except DeadlineExceededError:
            self.response.clear()
            self.response.set_status(500)
            logger.info("Except DeadlineExceeded Error")
            error = "We had a problem processing your request, pleae try again"
            venues = None
        except Exception, e:
            self.response.clear()
            self.response.set_status(500)
            logger.info("Except %s", e)
            error = "We had a problem processing your request, pleae try again"
            venues = None

        params = {}
        params['enquirykey'] = enquirykey
        if venues and package:
            accom_element.availableBerths = str(venues)
            accom_element.put()
            params = urllib.urlencode(params)
            self.redirect('/bookings/enquiry/viewenquiry?%s' % params)
        elif not venues:
            #Clean up
            accom_element.availableBerths = None
            accom_element.put()
            if enquiry.workflowStateName not in \
                    ['onhold', 'awaitingagent', 'expired']:
                enquiry.doTransition('putonhold')
            if not error:
                error = "No results found" 
            params['error'] = error
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

