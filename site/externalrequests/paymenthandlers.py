import os
from datetime import datetime
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import datastore_errors
from google.appengine.api import users

from xml.etree.ElementTree import Element, SubElement, tostring

from models.bookinginfo import \
        EnquiryCollection, Enquiry, \
        AccommodationElement, GuestElement, \
        CollectionPaymentTracker, EnquiryPaymentTracker, VCSPaymentNotification

from models.clientinfo import Client
from models.codelookup import getItemDescription

from controllers import generator
# from workflow.__init__ import ENQUIRY_WORKFLOW


class PaymentNotification(webapp.RequestHandler):
    """ Handler class for all enquiry/booking requests from
        the pulic sites.
    """
    def _addErrorNode(self, node, code='0', message=None):
        error_element = SubElement(node, 'systemerror')
        error_code = SubElement(error_element, 'errorcode')
        error_code.text = code
        error_msg = SubElement(error_element, 'errormessage')
        if message is not None:
            error_msg.text = message


    def _populateNotification(self, pay_rec):
        """ Populate the VCS payment record from the request
        """
        pay_rec.creator = users.get_current_user()
        pay_rec.timeStamp = datetime.strptime(self.request.get('timestamp'), 
                                                '%Y-%m-%d %H:%M').datetime()

        pay_rec.terminalId = self.request.get('p1')
        pay_rec.txRefNum =  self.request.get('p2')
        pay_rec.txType =  self.request.get('TransactionType')
        pay_rec.duplicateTransaction =  self.request.get('p4').tolower() == 'duplicate'
        auth_str = self.request.get('p3')
        if pay_rec.txType == 'Authorisation':
            if auth_str.rstrip()[6:] == 'APPROVED':
                pay_rec.authorised = True
                pay_rec.authNumberOrReason = auth_str[:6]
            else:
                pay_rec.authorised = False
                pay_rec.authNumberOrReason = auth_str.strip()
        pay_rec.authResponseCode =  self.request.get('p12')

        pay_rec.goodsDescription =  self.request.get('p8')
        pay_rec.authAmount =  float(self.request.get('p6'))
        pay_rec.budgetPeriod =  self.request.get('p10')

        pay_rec.cardHolderName =  self.request.get('p5')
        pay_rec.cardHolderEmail =  self.request.get('p9')
        pay_rec.cardHolderIP =  self.request.get('CardHolderIpAddr')

        pay_rec.maskedCardNumber =  self.request.get('MaskedCardNumber')
        pay_rec.cardType =  self.request.get('p7')
        pay_rec.cardExpiry =  self.request.get('p11')

        pay_rec.pam =  self.request.get('pam')

        pay_rec.enquiryCollection =  self.request.get('m_1')
        pay_rec.enquiryList = []
        for num in self.request.get('m_2').split(','):
            enq_num = num[:3] + '-' + num[3:6] + '-' + num[6:]
            pay_rec.enquiryList.append(enq_num)

        pay_rec.paymentType =  self.request.get('m_3')
        pay_rec.depositPercentage =  int(self.request.get('m_4'))



    def post(self):
        """ Primary interface for deposit payments
            coming from the public sites
        """
        # create a xml return node

        node = Element('paymentnotification')
        # creat the VCS payment record for the relevant
        # payment collection

        # get the enquiry collection associated with the payment
        enquiry_colection_number = self.request.get('m_3')
        enquiry_collection = EnquiryCollection.get_by_key_name( \
                                                        enquiry_colection_number)
        if not enquiry_collection:
            self._addErrorNode(node, code="301", 
                    message="Cannot find the enquiry collection: %s." % \
                                                    enquiry_colection_number)
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write(tostring(node))
            return

        # create or get the collection payment tracker 
        #    for the enquiry collection
        collection_tracker = CollectionPaymentTracker.get_or_insert( \
                                            key_name=enquiry_colection_number,
                                            parent=enquiry_collection)
        collection_tracker.creator = users.get_current_user()
        collection_tracker.put()
        collection_tracker.enterWorkflow(COLL_TRACK_PAY_WORKFLOW)
        
        # create the VCS payment record for the payment collection tracker
        pay_rec = VCSPaymentNotification(key_name=enquiry_colection_number,
                                         parent=collection_tracker)
        self._populateNotification(pay_rec)
        pay_rec.put()

        # TODO: 
        # 1. Create enquiry payment trackers for each enquiry and set their 
        #    workflow appropriately. 
        # 2. Set the workflow of the enquiry instance appropriately.
        # 3. Set the workflow of the collection tracker to the collective
        #    state of the enquiry payment trackers
 
        # return the result
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(tostring(node))


application = webapp.WSGIApplication([
                  ('/paymentnotify', PaymentNotification),
                  ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
