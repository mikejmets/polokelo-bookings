import logging
from google.appengine.api import mail

logger = logging.getLogger('EmailTool')


class EmailTool():

  def notifyClientOfAllocation(self, enquiry, element):
      message = mail.EmailMessage()
      message.sender = 'mike@metcalfe.co.za'
      message.to = 'mikejmets@gmail.com'
      message.subject="Enquiry has been allocated"
      message.body = u"""
      Thank you for your enquiry about accommodation
      Venue Type: %s
      From: %s
      Nights: %s
      """ % (element.type, 
             element.start,
             element.nights)
      try:
          # message.check_initialized()
          message.send()
          logger.info('Send notification email to client %s', message.to)
      except InvalidAttachmentTypeError:
          logger.debug('Invalid Attachment')
      except MissingRecipientsError:
          logger.debug('Missing Recipients')
      except MissingSenderError:
          logger.debug('Missing Sender')
      except MissingSubjectError:
          logger.debug('Missing Subject')
      except MissingBodyError:
          logger.debug('Missing Body')
      except PayloadEncodingError:
          logger.debug('Payload encoding error')
      except UnknownEncodingError:
          logger.debug('Unknown encoding error')
      except UnknownCharsetError:
          logger.debug('Unknown character set')
      except BadRequestError:
          logger.debug('Bad Request')
      except InvalidSenderError:
          logger.debug('Invalid Sender')
      except:
          logger.debug(sys.exc_info()[1])

