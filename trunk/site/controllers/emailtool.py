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
        logger.info('Notify Client: %s', recipients)
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
        except:
            email.delete()
            status = str(sys.exc_info()[1])
            raise

    def getBodyFromAction(self, action, element):
        subject = u""
        body = u""
        if action in ['receivedetails']:
            subject = u"Polokelo enquiry notification - ref %s" % \
                element.parent().referenceNumber
            body = u"""
We have received your details, your booking will be held until %s
            """ % element.parent().expiryDate
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
                       element.parent().referenceNumber, 
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
http://www.polokelo.info/getinvoice?ref=%s
                """ % \
                       element.parent().referenceNumber
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
        message.sender = 'bookings@polokelo-bookings.co.za'
        message.reply_to = 'bookings@polokelo-bookings.co.za'
        message.bcc = 'bookings@polokelo-bookings.co.za'
        try:
            message.subject = email.subject
            message.body = email.body
            # message.check_initialized()
            message.send()
            logger.info('Send notification email to client %s', message.to)
        except:
            status = str(sys.exc_info()[1])

        return status
