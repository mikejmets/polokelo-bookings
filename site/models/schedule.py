from google.appengine.ext import db

class Match(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    number = db.StringProperty(
        required=True, verbose_name='Match Number')
    date = db.DateTimeProperty(
        required=True, verbose_name='Match Date and Time')
    city = db.StringProperty(
        required=True, verbose_name='City')
    stadium = db.StringProperty(
        required=True, verbose_name='Stadium')

    def listing_name(self):
        return "%s, %s, %s, %s" %  \
          (self.number, self.date, self.city, self.stadium)

    def rdelete(self):
        self.delete()

