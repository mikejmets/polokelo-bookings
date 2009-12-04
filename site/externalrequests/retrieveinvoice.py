import os
import sys
import logging
from xml.etree.ElementTree import XML, SubElement, tostring

from models.enquiryroot import EnquiryRoot
from models.bookinginfo import EnquiryCollection, CollectionTransaction, \
                                Enquiry, AccommodationElement, GuestElement


def _addErrorNode(node, code='0', message=None):
    error_element = SubElement(node, 'systemerror')
    error_code = SubElement(error_element, 'errorcode')
    error_code.text = code
    error_msg = SubElement(error_element, 'errormessage')
    if message is not None:
        error_msg.text = message

def _getCardHolderDetails(collection):
    """ return the credit card holder details xml node 
        from the original xml source of the enquiry
    """
    guest_node = GuestElement.all().ancestor(collection).get()
    if guest_node:
        source = guest_node.xmlSource
        logging.info('xml source: %s', source)
        xml = XML(source)
        return xml

def retrieveInvoice(node):
    """ retrieve the invoice details given the batch number
    """
    # TODO: return error codes as per Johan's suggestion
    # TODO: clean up error codes in general

    logging.info('entering retrieveInvoice')
    enquiry_root = EnquiryRoot.getEnquiryRoot()

    # get the enquiry collection
    collection_number = node.findtext('enquirybatchnumber')
    logging.info('retrieveInvoice batch number: %s', collection_number)
    try:
        enquiry_collection = EnquiryCollection.get_by_key_name(collection_number, \
                                                           parent=enquiry_root)
        # get the credit card holder details from a
        # confirmed or paid enquiry on the collection
        card_holder_node = _getCardHolderDetails(enquiry_collection)
        if card_holder_node:
            node.append(card_holder_node)

        # get the line items
        items_node = SubElement(node, 'items')

        # get all the enquiries of this collection
        qry = Enquiry.all().ancestor(enquiry_collection)
        qry.filter('workflowState in', 
                ['detailsreceieved', 'depositpaid', 'paidinfull'])
        enquiries = qry.fetch(10)
        for enquiry in enquiries:
            item_node = SubElement(items_node, 'item')
            new_node = SubElement(item_node, 'enquirynumber')
            new_node.text = enquiry.referenceNumber
            new_node = SubElement(item_node, 'description')
            new_node.text = enquiry.getAccommodationDescription()
            new_node = SubElement(item_node, 'qty')
            new_node.text = '1'
            new_node = SubElement(item_node, 'amount')
            new_node.text = "%0.2f" % (enquiry.quoteInZAR / 100.0)
            new_node = SubElement(item_node, 'vat')
            new_node.text = "%0.2f" % (enquiry.vatInZAR / 100.0)

        # get the applicable payment transactions
        items = CollectionTransaction.all().ancestor(enquiry_collection)
        items.order('created')
        items.filter('type =', 'Payment')
        for item in items:
            item_node = SubElement(items_node, 'item')
            new_node = SubElement(item_node, 'enquirynumber')
            new_node = SubElement(item_node, 'description')
            new_node.text = item.description
            new_node = SubElement(item_node, 'qty')
            new_node.text = '1'
            new_node = SubElement(item_node, 'amount')
            new_node.text = "%0.2f" % (item.total / 100.0)
            new_node = SubElement(item_node, 'vat')

    except:
        error = sys.exc_info()[1]
        logging.error('Unhandled error: %s', error)
        _addErrorNode(node, code='4001', \
                        message='Seriously Unexpected and Unhandleable Error')

    return tostring(node)


if __name__ == '__main__':
    pass
