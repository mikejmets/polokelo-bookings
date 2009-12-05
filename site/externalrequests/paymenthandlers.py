import os
import sys
import logging
from datetime import datetime
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import datastore_errors
from google.appengine.api import users
from google.appengine.ext.db import run_in_transaction

from xml.etree.ElementTree import Element, SubElement, tostring
from exceptions import Exception

from models.enquiryroot import EnquiryRoot
from models.bookinginfo import \
                EnquiryCollection, Enquiry, \
                CollectionTransaction, VCSPaymentNotification

from models.clientinfo import Client
from models.codelookup import getItemDescription

from controllers import generator


class EnquiryDoesNotExistException(Exception):
    """ Enquiry instance for a collection is not found
    """
    pass

class AppliedAmountDiscrepancyException(Exception):
    """ Raise the exception if the amounts applied to each
        enquiry does not add up to the VCS payment record total
    """
    pass


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
        try:
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
        except Exception:
            pay_rec.processingState = 'Failed'
            pay_rec.put()
            error = sys.exc_info()[1]
            logging.error('Unhandled error: %s', error)



    def _applyfunds(self, pay_rec, enquiry_collection):
        """ apply the funds from the payment record to the individual
            enquiry objects. Create a transaction record on the collection
        """
        # start with the total amount available on the payment
        # and subtract each applied amount until we have handled all the
        # enquiries, and check for discrepancies at the end, and raise an
        # exception if applicable
        available_total = pay_rec.authAmount
        
        # the payment transaction description and amounts
        txn_description = 'Payment on %s: REFERENCE %s\n' % \
                            (datetime.now().date(), enquiry_collection.referenceNumber)
        txn_total = 0L

        # Update and set the workflow of the enquiry instance appropriately.
        for enquiry_number in pay_rec.enquiryList:
            enquiry = Enquiry.get_by_key_name(enquiry_number, 
                                              parent=enquiry_collection)
            if enquiry:
                logging.info('Found enquiry %s', enquiry_number)

                if pay_rec.paymentType == u'DEP' and \
                                enquiry.getStateName() == 'confirmed':
                    logging.info('Transition receivedeposit for %s', enquiry_number)
                    applied_amount = long(enquiry.totalAmountInZAR * \
                                            (pay_rec.depositPercentage / 100.0))
                    transition_name = 'receivedeposit'
                    txn_description += 'Accom REF %s: %d%% Deposit\n' % \
                            (enquiry_number, pay_rec.depositPercentage)

                elif pay_rec.paymentType == u'INV' and \
                        (enquiry.getStateName() in ['receiveddeposit', 'confirmed']):
                    logging.info('Transition receivefinal for %s', 
                        enquiry_number)
                    applied_amount = enquiry.totalAmountInZAR - \
                                            enquiry.amountPaidInZAR
                    if enquiry.getStateName() == 'receiveddeposit':
                        transition_name = 'receivefinal'
                    elif enquiry.getStateName() == 'confirmed': 
                        transition_name = 'receiveall'
                    txn_description += 'Accom REF %s: Outstanding Balance\n' % \
                                                        (enquiry_number)

                available_total -= applied_amount
                txn_total += applied_amount

                # check that applying the amount won't raise a discrepancy
                if available_total < 0:
                    logging.info('available_total: %s', available_total)
                    raise AppliedAmountDiscrepancyException, \
                                    enquiry_collection.referenceNumber
                enquiry.amountPaidInZAR += applied_amount
                enquiry.put()
                enquiry.doTransition(transition_name)
            else:
                # we have a rogue enquiry on the payment
                raise EnquiryDoesNotExistException, enquiry_number

        # check if we have any money left over, indicating too big a payment was made
        if available_total > 0:
            logging.info('available_total: %s', available_total)
            raise AppliedAmountDiscrepancyException, enquiry_collection.referenceNumber

        # create the payment transaction in the collection
        txn = CollectionTransaction(parent=enquiry_collection)
        txn.type = 'Payment'
        txn.creator = users.get_current_user()
        txn.description = txn_description
        txn.total = -1 * txn_total
        txn.put()

        # change the processing status of the payment record
        pay_rec.processingState = 'Completed'
        pay_rec.put()


    def post(self):
        """ Primary interface for deposit payments
            coming from the public sites
        """
        # create a xml return node
        node = Element('paymentnotification')

        # get the enquiry collection associated with the payment
        enquiry_colection_number = self.request.get('m_1') or 'unknown'
        enquiry_collection = EnquiryCollection.get_by_key_name( \
                                                enquiry_colection_number,
                                                parent=EnquiryRoot.getEnquiryRoot())
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

        # check that the processing of the payment notification did not fail
        if pay_rec.processingState == 'Failed':
            SubElement(node, 'payment')
            self._addErrorNode(node, code='303',
                    message='Could not successfully process the VCS transaction data. Money was not applied to the enquiries.')
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write(tostring(node))
            return

        # check that the payment transaction is state authorised and not a duplicate
        if not pay_rec.duplicateTransaction and \
                pay_rec.txType == u'Authorisation' and \
                pay_rec.authorised:
            try:
                run_in_transaction(self._applyfunds, pay_rec, enquiry_collection) 

            except EnquiryDoesNotExistException, enquiry_number:
                pay_rec.processingState = 'Failed'
                pay_rec.put()
                SubElement(node, 'payment')
                self._addErrorNode(node, code='303',
                    message='Enquiry %s, referenced on payment %s, does not exist'\
                            % (enquiry_number, enquiry_colection_number))
                self.response.headers['Content-Type'] = 'text/plain'
                self.response.out.write(tostring(node))
                return

            except AppliedAmountDiscrepancyException, enquiry_number:
                pay_rec.processingState = 'Failed'
                pay_rec.put()
                SubElement(node, 'payment')
                self._addErrorNode(node, code='304',
                    message='Payment %s, received amount does not add up to outstanding amounts on enquiries' % (enquiry_colection_number))
                self.response.headers['Content-Type'] = 'text/plain'
                self.response.out.write(tostring(node))
                return

            except:
                pay_rec.processingState = 'Failed'
                pay_rec.put()
                error = sys.exc_info()[1]
                logging.error('Unhandled error: %s', error)
                SubElement(node, 'payment')
                self._addErrorNode(node, code='3001', \
                                message='Seriously Unexpected and Unhandleable Error')
                self.response.headers['Content-Type'] = 'text/plain'
                self.response.out.write(tostring(node))
                return

        else:
            SubElement(node, 'payment')
            self._addErrorNode(node, code='302',
                    message='Transaction not authorised, or duplicate')
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write(tostring(node))
            return
 
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
