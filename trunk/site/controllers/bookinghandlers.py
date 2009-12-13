import os
import urllib
import logging
from datetime import datetime
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.utils import get_authentication_urls
from controllers.contractedbooking import \
    AssignClientToBooking, \
    ViewContractedBooking, CaptureContractedBooking, \
    EditContractedBooking, DeleteContractedBooking
from controllers.enquiry import \
    ViewEnquiry, AdvanceEnquiry, \
    BookingsToolFindAccommodation, BookingsToolReserveAccommodation, \
    CaptureEnquiry, EditEnquiry, DeleteEnquiry
from controllers.enquirycollection import ViewEnquiryCollection, \
    CaptureEnquiryCollection, EditEnquiryCollection, DeleteEnquiryCollection, \
    ViewVCSRecord, ViewTransactionRecord, \
    CaptureTransactionRecord, EditTransactionRecord, DeleteTransactionRecord
from models.bookinginfo import EnquiryCollection, ContractedBooking
from controllers.bookingsemail import \
    CaptureBookingsEmail, EditBookingsEmail, DeleteBookingsEmail
from controllers.guestelements import \
        ViewGuestElement, CaptureGuestElement, EditGuestElement

from controllers import generator
from controllers.utils import get_authentication_urls

logger = logging.getLogger('BookingHandlers')

class ManageBookings(webapp.RequestHandler):
    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        contractedbookings = ContractedBooking.all().order('bookingNumber')
        collections = EnquiryCollection.all().order('referenceNumber')

        filepath = os.path.join(
            PROJECT_PATH, 'templates', 'bookings', 'managebookinginfo.html')
        extras = {'base_path':BASE_PATH,
                  'contractedbookings':contractedbookings,
                  'collections':collections,
                  'user':users.get_current_user(),
                  'auth_url':auth_url,
                  'auth_url_text':auth_url_text
                  }
        self.response.out.write(template.render(filepath, extras))


class BookingError(webapp.RequestHandler):
    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        error =  self.request.get('error')
        enquirykey =  self.request.get('enquirykey')

        filepath = os.path.join(
            PROJECT_PATH, 'templates', 'bookings', 'bookingerror.html')
        extras= { 'base_path':BASE_PATH,
                  'error':error,
                  'enquirykey':enquirykey,
                  'user':users.get_current_user(),
                  'auth_url':auth_url,
                  'auth_url_text':auth_url_text
                  }
        self.response.out.write(
            template.render(filepath, extras))

    def post(self):
        came_from = '/bookings/enquiry/viewenquiry'
        params = {}
        params['enquirykey'] = self.request.get('enquirykey')
        params = urllib.urlencode(params)
        self.redirect('%s?%s' % (came_from, params))


application = webapp.WSGIApplication([
      ('/bookings/bookinginfo', ManageBookings),
      ('/bookings/bookingerror', BookingError),
      ('/bookings/assignclient', AssignClientToBooking),
      ('/bookings/viewcontractedbooking', ViewContractedBooking),
      ('/bookings/capturecontractedbooking', CaptureContractedBooking),
      ('/bookings/editcontractedbooking', EditContractedBooking),
      ('/bookings/deletecontractedbooking', DeleteContractedBooking),
      ('/bookings/collection/viewenquirycollection', ViewEnquiryCollection),
      ('/bookings/collection/captureenquirycollection', CaptureEnquiryCollection),
      ('/bookings/collection/editenquirycollection', EditEnquiryCollection),
      ('/bookings/collection/deleteenquirycollection', DeleteEnquiryCollection),
      ('/bookings/collection/viewvcsrecord', ViewVCSRecord),
      ('/bookings/collection/viewtxnrecord', ViewTransactionRecord),
      ('/bookings/collection/capturetxnrecord', CaptureTransactionRecord),
      ('/bookings/collection/edittxnrecord', EditTransactionRecord),
      ('/bookings/collection/deletetxnrecord', DeleteTransactionRecord),
      ('/bookings/enquiry/viewenquiry', ViewEnquiry),
      ('/bookings/enquiry/advanceenquiry', AdvanceEnquiry),
      ('/bookings/enquiry/captureenquiry', CaptureEnquiry),
      ('/bookings/enquiry/editenquiry', EditEnquiry),
      ('/bookings/enquiry/deleteenquiry', DeleteEnquiry),
      ('/bookings/enquiry/findaccommodation', BookingsToolFindAccommodation),
      ('/bookings/enquiry/reserveaccommodation', BookingsToolReserveAccommodation),
      ('/bookings/email/captureemail', CaptureBookingsEmail),
      ('/bookings/email/editemail', EditBookingsEmail),
      ('/bookings/email/deleteemail', DeleteBookingsEmail),
      ('/bookings/guests/viewguest', ViewGuestElement),
      ('/bookings/guests/captureguest', CaptureGuestElement),
      ('/bookings/guests/editguest', EditGuestElement),
    ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
