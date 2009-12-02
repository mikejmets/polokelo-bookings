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
        VCSPaymentNotification

from models.clientinfo import Client
from models.codelookup import getItemDescription

from controllers import generator


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
                                                '%Y-%m-%d %H:%M')

        pay_rec.terminalId = self.request.get('p1')
        pay_rec.txRefNum =  self.request.get('p2')
        pay_rec.txType =  self.request.get('TransactionType')
        pay_rec.duplicateTransaction =  self.request.get('p4') == u'DUPLICATE'
        pay_rec.authResponseCode =  self.request.get('p12')
        auth_str = self.request.get('p3')
        if pay_rec.txType == u'Authorisation':
            if pay_rec.authResponseCode == u'00' or \
                    pay_rec.authResponseCode == u'0' or \
                    auth_str.rstrip()[6:] == u'APPROVED':
                pay_rec.authorised = True
                pay_rec.authNumberOrReason = auth_str[:6]
            else:
                pay_rec.authorised = False
                pay_rec.authNumberOrReason = auth_str.strip()

        pay_rec.goodsDescription =  self.request.get('p8')
        amount = float(self.request.get('p6'))
        iAmount = long(amount * 100.0)       # convert into cents
        pay_rec.authAmount = iAmount
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

        # get the enquiry collection associated with the payment
        enquiry_colection_number = self.request.get('m_1')
        enquiry_collection = EnquiryCollection.get_by_key_name( \
                                                        enquiry_colection_number)
        if not enquiry_collection:
            SubElement(node, 'payment')
            self._addErrorNode(node, code="301", 
                    message="Cannot find the enquiry collection: %s." % \
                                                    enquiry_colection_number)
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write(tostring(node))
            return

        # create and add the VCS payment record for the enquiry collection
        pay_rec = VCSPaymentNotification(parent=enquiry_collection)
        self._populateNotification(pay_rec)
        pay_rec.put()

        # keep track of amounts paid in cents
        deposit_total = 0L
        outstanding_total = 0L

        # Update and set the workflow of the enquiry instance appropriately.
        for enquiry_number in pay_rec.enquiryList:
            enquiry = Enquiry.get_by_key_name(enquiry_number, 
                                              parent=enquiry_collection)
            if enquiry:
                logging.info('Found enquiry %s', enquiry_number)
                if not pay_rec.duplicateTransaction and \
                        pay_rec.txType == u'Authorisation' and \
                        pay_rec.authorised:

                    if pay_rec.paymentType == u'DEP' and \
                                    enquiry.getStateName() == 'detailsreceieved':
                        logging.info('Transition paydeposit for %s', enquiry_number)
                        enquiry.doTransition('paydeposit', 
                                    deposit_percentage=pay_rec.depositPercentage/100.0)
                        deposit_total += enquiry.amountPaidInZAR
                    elif pay_rec.paymentType == u'INV' and \
                                    enquiry.getStateName() == 'depositpaid':
                        logging.info('Transition payfull for %s', enquiry_number)
                        outstanding_total -= enquiry.amountPaidInZAR
                        enquiry.doTransition('payfull')
                        outstanding_total += enquiry.amountPaidInZAR
                    # TODO: create transaction entries on the collection
                else:
                    SubElement(node, 'payment')
                    self._addErrorNode(node, code='302',
                            message='Transaction not authorised, or duplicate')
                    self.response.headers['Content-Type'] = 'text/plain'
                    self.response.out.write(tostring(node))
                    return
            else:
                SubElement(node, 'payment')
                self._addErrorNode(node, code='303',
                    message='Enquiry %s, referenced on payment %s, does not exist'\
                            % (enquiry_number, enquiry_colection_number))
                self.response.headers['Content-Type'] = 'text/plain'
                self.response.out.write(tostring(node))
                return

        # check that the amounts add up
        if pay_rec.authAmount != (deposit_total + outstanding_total):
            logging.error("%f, %f", pay_rec.authAmount, deposit_total + outstanding_total )
            SubElement(node, 'payment')
            self._addErrorNode(node, code='304',
                message='Payment %s, received amount does not add up to outstanding amounts on enquiries' % (enquiry_colection_number))
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write(tostring(node))
            return
        else:
            # TODO: store discrepancy somewhere
            pass

 
        # return the result
        result_node = SubElement(node, 'payment')
        batch_node = SubElement(result_node, 'enquirybatchnumber')
        batch_node.text = enquiry_colection_number
        self._addErrorNode(node)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(tostring(node))


application = webapp.WSGIApplication([
                  ('/paymentnotify', PaymentNotification),
                  ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
