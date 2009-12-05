import sys
import logging
from google.appengine.api import mail
from models.bookingsemail import BookingsEmail

logger = logging.getLogger('EmailTool')


class EmailTool():

    def notifyClient(self, action, element):
        subject, body = self.getBodyFromAction(action, element)
        logger.info('Notify Client: %s, %s, %s', 
            action, subject, body)
        recipients = []
        if element.parent().guestEmail:
            recipients.append(str(element.parent().guestEmail))
        logger.info('Notify recipients: %s', recipients)
        email = BookingsEmail(
            parent=element.parent(),
            recipients = recipients,
            subject = subject,
            body = body,
            action = action)
        #Send
        try:
            email.status = self.sendEmail(email, element)
            email.put()
        except Exception, e:
            logger.info('Exception in NotifyClient: %s', e)
            email.delete()
            status = str(sys.exc_info()[1])
            raise Exception, e

    def getBodyFromAction(self, action, element):
        subject = u""
        body = u""
        if action in ['confirmfromallocated', 'confirmfromawaiting']:
            subject = u"Polokelo enquiry notification - ref %s" % \
                element.parent().referenceNumber
            body = u"""
Thank you for confirming your booking, it will be held until %s (GMT+2).
            """ % element.parent().expiryDate
        elif action in ['expireconfirmed']:
            subject = u"Polokelo enquiry notification - ref %s" % \
                element.parent().referenceNumber
            body = u"""
We regret to imform you that your booking has expired.
            """ 
        elif action in ['expiredeposit']:
            subject = u"Polokelo enquiry notification - ref %s" % \
                element.parent().referenceNumber
            body = u"""
We regret to imform you that your booking has expired and 
you have lost your deposit.
            """ 
        elif action in ['receivedeposit']:
            subject = u"Polokelo enquiry notification - ref %s" % \
                element.parent().referenceNumber
            body = u"""
Thank you for your deposit. Please not that unless the balance is paid
by %s (GMT+2), the booking will expire.
            """ % element.parent().expiryDate
        elif action in ['assigntoclient']:
            subject = u"Polokelo enquiry notification - ref %s" % \
                element.parent().referenceNumber
            body = u"""
We have managed to find the accommodation you requested. If you would
like to proceed with your bookings, please click on the link below.
Note that this booking will expire at %s (GMT+2).
            """ % element.parent().expiryDate
        elif action in ['receiveall']:
            subject = u"Polokelo enquiry notification - ref %s" % \
                element.parent().referenceNumber
            body = u"""
Thank you for your complete payment. Looking forward to seeing you.
            """ 
        elif action in ['receivefinal']:
            subject = u"Polokelo enquiry notification - ref %s" % \
                element.parent().referenceNumber
            body = u"""
Thank you for your final payment. Looking forward to seeing you.
            """ 
        else:
            subject = u"Polokelo enquiry notification - ref %s" % \
                element.parent().referenceNumber
            body = u"""
Thank you for your enquiry about accommodation
            """ 
        return subject, body

    def getEnquirySummary(self, element):
            summary = u''
            if element:
                summary = u"""
Enquiry Summary:
    Reference Number: %s
    Venue Type:       %s
    From Date         %s
    Nights:           %s
    People:           %s
                """ % (
                       element.parent().parent().referenceNumber, 
                       element.type, 
                       element.start,
                       element.nights,
                       element.adults + element.children,
                       )
            return summary

    def getEnquiryLink(self, element):
            link = u''
            if element:
              link = u"""
Click on the following link to see you invoice:
http://www.polokelo.info/getinvoice.php?ref=%s
                """ % \
                       element.parent().parent().referenceNumber
            return link

    def sendEmail(self, email, element):
        status = 'Sent'
        body = email.body
        if email.includeSummary:
            body = "%s\n%s" % (body, self.getEnquirySummary(element))
        if email.includeLink:
            body = "%s\n%s" % (body, self.getEnquiryLink(element))
        email.body = body
        email.put()
        message = mail.EmailMessage()
        message.to = email.recipients
        message.sender = 'polokelo123@gmail.com'
        message.reply_to = 'polokelo123@gmail.com'
        message.bcc = 'mike@yourbookings.co.za'
        try:
            message.subject = email.subject
            message.body = email.body
            # message.check_initialized()
            message.send()
            logger.info('Send notification email to client %s', message.to)
        except:
            status = str(sys.exc_info()[1])

        return status
