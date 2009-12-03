from google.appengine.ext import db

class BookingsEmail(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    recipients = db.StringListProperty(required=True, verbose_name='Recipients')
    subject = db.TextProperty(required=True, verbose_name='Subject')
    body = db.StringProperty(required=True, multiline=True, verbose_name='Body')
    includeSummary = db.BooleanProperty(
        verbose_name='Include Enquiry Summary', default=True)
    includeLink = db.BooleanProperty(
        verbose_name='Include Website Link', default=True)
    status = db.StringProperty(verbose_name='Status')
    action = db.StringProperty()

    def listing_name(self):
        recipient = ""
        if len(self.recipients) > 0:
            recipient = self.recipients[0]
        return "%s: %s, %s, %s" % (
            self.status, recipient, self.subject, self.action)

    def rdelete(self):
        self.delete()

