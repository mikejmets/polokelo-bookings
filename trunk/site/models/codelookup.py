from google.appengine.ext import db

class CodeLookup(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    shortcode = db.StringProperty(verbose_name='Item Short Code', required=True)
    container = db.StringProperty(verbose_name='Item Container Code', required=True, default='root')
    description = db.StringProperty(verbose_name='Item Description', required=True)
    sort_order = db.IntegerProperty(verbose_name='Sort Order if Required', default=0)

    def lookupItems(self):
        items = CodeLookup.all()
        items.filter('container =', self.shortcode)
        items.order('sort_order')
        return items

    def rdelete(self):
        items = self.lookupItems()
        for item in items:
            item.rdelete()
        self.delete()

