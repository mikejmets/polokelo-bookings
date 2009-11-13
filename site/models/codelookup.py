from google.appengine.ext import db

class CodeLookup(db.Model):
    """ implements a simple lookup mechanism based on codes
        mainly used to populate drop down items and inter
        site communication structures
    """
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    shortcode = db.StringProperty(verbose_name='Item Short Code', required=True)
    container = db.StringProperty(verbose_name='Item Container Code', 
                                required=True, default='root')
    description = db.StringProperty(verbose_name='Item Description', required=True)
    sort_order = db.IntegerProperty(verbose_name='Sort Order if Required', default=0)
    state = db.StringProperty(verbose_name='Activation State', default='active', 
                                choices=['draft', 'active', 'obsolete'], required=True)

    def lookupItems(self):
        """ use in the admin system for editing purposes
        """
        items = CodeLookup.all()
        items.filter('container =', self.shortcode)
        items.order('sort_order')
        return items

    def lookupItemDescription(self, parentcode, itemcode):
        """ retrieve the long description of any item or lookuptable 
            in active or obsolete state
            for external use.
        """
        items = CodeLookup.all()
        items.filter('container =', parentcode)
        items.filter('shortcode =', itemcode)
        items.filter('state in', ['active', 'obsolete'])
        return '|'.join([item.description for item in items])

    def rdelete(self):
        """ use in the admin system to flag item as obsolete
            i.e. should no longer be presented for external use
        """
        items = self.lookupItems()
        for item in items:
            item.rdelete()
        self.state = 'obsolete'
        self.put()

    def activeLookupTables(self):
        """ get a list of the root lookuptable items
            for non-admin site use
        """
        items = CodeLookup.all()
        items.filter('container =', 'root')
        items.filter('state =', 'active')
        items.order('sort_order')
        return items

    def activeLookupItems(self):
        """ get a list of items in a lookuptable
            for non-admin site use
        """
        items = CodeLookup.all()
        items.filter('container =', self.shortcode)
        items.filter('state =', 'active')
        items.order('sort_order')
        return items
