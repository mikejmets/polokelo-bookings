import os
import urllib
import logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from django import newforms as forms
from google.appengine.ext import db

from controllers.home import BASE_PATH, PROJECT_PATH
from models.enquiryroot import EnquiryRoot
from models.bookinginfo import EnquiryCollection, Enquiry, \
                VCSPaymentNotification, CollectionTransaction, GuestElement
from controllers.utils import get_authentication_urls
from controllers import generator

logger = logging.getLogger('EnquiryCollectionHandler')


class EnquiryCollectionForm(djangoforms.ModelForm):
    class Meta:
        model = EnquiryCollection
        exclude = ['created', 'creator']


class ViewEnquiryCollection(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'bookings', 'viewenquirycollection.html')
        enquirycollectionkey = self.request.get('enquirycollectionkey')
        enquirycollection = EnquiryCollection.get(enquirycollectionkey)
        enquiries = Enquiry.all().ancestor(enquirycollection).order('created')
        vcsrecords = VCSPaymentNotification.all().ancestor(enquirycollection)
        vcsrecords.order('created')
        qry = GuestElement.all().ancestor(enquirycollection)
        qry.filter('isPrimary =', True).order('created')
        card_holder = qry.get()
        qry = CollectionTransaction.all().ancestor(enquirycollection).order('created')
        transactions = []
        for txn in qry:
            transactions.append({
                'txnkey':txn.key(),
                'enquiryReference':txn.enquiryReference,
                'created':txn.created,
                'type':txn.type,
                'subType':txn.subType,
                'total':'%0.2f' % (txn.total / 100.0),
                'can_edit':txn.category != 'Auto'})
        self.response.out.write(template.render(filepath, 
              {
                  'base_path':BASE_PATH,
                  'enquirycollectionkey': enquirycollectionkey,
                  'enquirycollection': enquirycollection,
                  'enquiries':enquiries,
                  'vcsrecords':vcsrecords,
                  'transactions':transactions,
                  'cardholder':card_holder,
                  'user':users.get_current_user(),
                  'auth_url':auth_url,
                  'auth_url_text':auth_url_text
                  }))

    def post(self):
        transition = self.request.get('transition')
        enquirycollectionkey = self.request.get('enquirycollectionkey') 
        enquirycollection = EnquiryCollection.get(enquirycollectionkey)
        params = {}
        params['enquirycollectionkey'] = enquirycollectionkey 
        params = urllib.urlencode(params)
        self.redirect('/bookings/enquiry/viewenquirycollection?%s' % params)

class CaptureEnquiryCollection(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        er = EnquiryRoot.getEnquiryRoot()
        coll_num=generator.generateEnquiryCollectionNumber()
        collection = EnquiryCollection(key_name=coll_num, \
                                            parent=er, referenceNumber=coll_num)
        collection.put()
        self.redirect('/bookings/collection/viewenquirycollection?enquirycollectionkey=%s' % collection.key())



class EditEnquiryCollection(webapp.RequestHandler):

    def get(self):
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        came_from = self.request.referer
        enquirycollectionkey = self.request.get('enquirycollectionkey')
        enquirycollection = EnquiryCollection.get(enquirycollectionkey)
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'bookings', 'editenquirycollection.html')
        self.response.out.write(template.render(filepath, 
              {
                  'base_path':BASE_PATH,
                  'form':EnquiryCollectionForm(instance=enquirycollection),
                  'enquirycollectionkey':enquirycollectionkey,
                  'came_from':came_from,
                  'enquirycollectionkey':enquirycollectionkey,
                  'user':users.get_current_user(),
                  'auth_url':auth_url,
                  'auth_url_text':auth_url_text
                  }))

    def post(self):
        enquirycollectionkey = self.request.get('enquirycollectionkey')
        enquirycollection = EnquiryCollection.get(enquirycollectionkey)
        came_from = self.request.get('came_from')
        data = EnquiryCollectionForm(
                  data=self.request.POST, instance=enquirycollection)
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
                          'templates', 'bookings', 'editenquirycollection.html')
            self.response.out.write(template.render(filepath, 
                          {
                              'base_path':BASE_PATH,
                              'form':data,
                              'came_from':came_from,
                              'enquirycollectionkey':enquirycollectionkey
                              }))


class DeleteEnquiryCollection(webapp.RequestHandler):

    def get(self):
        enquirycollectionkey = self.request.get('enquirycollectionkey')
        enquirycollection = EnquiryCollection.get(enquirycollectionkey)
        if enquirycollection:
            #recursive delete
            logger.info('Delete collection %s', 
                enquirycollection.referenceNumber)
            enquirycollection.rdelete()

        self.redirect('/bookings/bookinginfo')


class ViewVCSRecord(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'bookings', 'viewvcsrecord.html')
        vcskey = self.request.get('vcskey')
        vcsrec = VCSPaymentNotification.get(vcskey)
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'came_from':came_from,
                        'vcsrec':vcsrec,
                        'auth_url':auth_url,
                        'auth_url_text':auth_url_text
                        }))


class ViewTransactionRecord(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                      'templates', 'bookings', 'viewtxnrecord.html')
        txnkey = self.request.get('txnkey')
        txn = CollectionTransaction.get(txnkey)
        transaction = {
                'created':txn.created,
                'enquiryReference':txn.enquiryReference,
                'type':txn.type,
                'subType':txn.subType,
                'description':txn.description,
                'notes':txn.notes,
                'cost':(txn.cost and '%0.2f' % (txn.cost / 100.0) or None),
                'vat':(txn.vat and '%0.2f' % (txn.vat / 100.0) or None),
                'total':(txn.total and '%0.2f' % (txn.total / 100.0) or '0.00')
                }
        
        self.response.out.write(template.render(filepath, 
                    {
                        'base_path':BASE_PATH,
                        'came_from':came_from,
                        'transaction':transaction,
                        'auth_url':auth_url,
                        'auth_url_text':auth_url_text
                        }))


class CollectionTransactionForm(djangoforms.ModelForm):
    class Meta:
        model = CollectionTransaction
        exclude = ['created', 'creator', 'category', 'cost', 'vat']

    enquiryReference = forms.ChoiceField(choices=[])



def _getEnquiryTuples(collection):
    """ Retrieve enquiries in a collection and return 
        a list suitable for a Django ChoiceField
    """
    enquiries = [('', '-- Select --'),
            (collection.referenceNumber, collection.referenceNumber)]
    enquiries.extend([(e.referenceNumber, e.referenceNumber) \
                                for e in Enquiry.all().ancestor(collection)])
    return enquiries


class CaptureTransactionRecord(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        coll_key = self.request.get('coll_key')
        theparent = EnquiryCollection.get(coll_key)
        enquiries = _getEnquiryTuples(theparent)
        tx_form = CollectionTransactionForm()
        tx_form.fields['enquiryReference'].choices = enquiries
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'bookings', 'capturetxnrecord.html')
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'coll_key':coll_key,
                                        'form':tx_form,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        coll_key = self.request.get('coll_key')
        theparent = EnquiryCollection.get(coll_key)
        data = CollectionTransactionForm(data=self.request.POST)
        valid = data.is_valid()
        if valid:
            clean_data = data._cleaned_data()
            total = clean_data.get('total') and \
                    int(clean_data.get('total')) or 0
            sub_type = clean_data.get('subType')
            if sub_type in ['Deposit', 'Settle', 'Payment', 'Unapplied']:
                if total > 0:
                    total = -1 * total
            elif sub_type in ['Refund', 'Shortfall']:
                if total < 0:
                    total = -1 * total
            txn = CollectionTransaction(parent=theparent,
                        subType = sub_type,
                        description = clean_data.get('description'),
                        enquiryReference = clean_data.get('enquiryReference'),
                        total=total)
            txn.creator = users.get_current_user()
            txn.type = clean_data.get('type')
            txn.category = 'Manual'
            txn.notes = clean_data.get('notes')
            txn.cost = int(total / 114.0 * 100.0)
            txn.vat = total - txn.cost
            txn.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                          'templates', 'bookings', 'capturetxnrecord.html')
            enquiries = _getEnquiryTuples(theparent)
            data.fields['enquiryReference'].choices = enquiries
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'coll_key':coll_key,
                                        'form':data,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class EditTransactionRecord(webapp.RequestHandler):

    def get(self):
        came_from = self.request.referer
        txnkey = self.request.get('txnkey')
        txn = CollectionTransaction.get(txnkey)
        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        filepath = os.path.join(PROJECT_PATH, 
                        'templates', 'bookings', 'edittxnrecord.html')
        enquiries = _getEnquiryTuples(txn.parent())
        tx_form = CollectionTransactionForm(instance=txn)
        tx_form.fields['enquiryReference'].choices = enquiries
        self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':tx_form,
                                        'txnkey':txnkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))

    def post(self):
        came_from = self.request.get('came_from')
        txnkey = self.request.get('txnkey')
        txn = CollectionTransaction.get(txnkey)
        data = CollectionTransactionForm(data=self.request.POST, instance=txn)
        if data.is_valid():
            entity = data.save(commit=False)
            if entity.subType in ['Deposit', 'Settle', 'Payment', 'Unapplied']:
                if entity.total > 0:
                    entity.total = -1 * entity.total
            elif entity.subType in ['Refund', 'Shortfall']:
                if entity.total < 0:
                    entity.total = -1 * entity.total
            entity.creator = users.get_current_user()
            entity.category='Manual'
            entity.cost = int(entity.total / 114.0 * 100.0)
            entity.vat = entity.total - entity.cost
            entity.put()
            self.redirect(came_from)
        else:
            auth_url, auth_url_text = get_authentication_urls(self.request.uri)
            filepath = os.path.join(PROJECT_PATH, 
                          'templates', 'bookings', 'edittxnrecord.html')
            enquiries = _getEnquiryTuples(txn.parent())
            data.fields['enquiryReference'].choices = enquiries
            self.response.out.write(template.render(filepath, 
                                    {
                                        'base_path':BASE_PATH,
                                        'form':data,
                                        'txnkey':txnkey,
                                        'came_from':came_from,
                                        'auth_url':auth_url,
                                        'auth_url_text':auth_url_text
                                        }))


class DeleteTransactionRecord(webapp.RequestHandler):
    def get(self):
        came_from = self.request.referer
        txn_key = self.request.get('txnkey')
        txn = CollectionTransaction.get(txn_key)
        txn.delete()
        self.redirect(came_from)
