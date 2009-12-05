from google.appengine.ext import db
from google.appengine.api import memcache

import logging

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

def getChoices(container):
    """ retrieve values to go into choices attributes of properties
    """
    result = None #memcache.get(container)
    if result is None:
        items = CodeLookup.all()
        items.filter('container =', container)
        items.filter('state =', 'active')
        items.order('sort_order')
        items.order('description')
        result = [item.description for item in items] 
        memcache.add(container, result)
    return result

def getChoicesTuple(container):
    """ retrieve values to go into choices attributes of properties
    """
    result = None #memcache.get(container)
    if result is None:
        items = CodeLookup.all()
        items.filter('container =', container)
        items.filter('state =', 'active')
        items.order('sort_order')
        items.order('description')
        result = [(item.description, item.description) for item in items] 
        memcache.add(container, result)
    return result

def getItemDescription(parentcode, itemcode):
    """ retrieve the long description of any item
        in active or obsolete state
        for external use.
    """
    result = memcache.get(itemcode, namespace='codelookup-description')
    if result is None:
        items = CodeLookup.all()
        items.filter('container =', parentcode)
        items.filter('shortcode =', itemcode)
        items.filter('state in', ['active', 'obsolete'])
        item_set = items.fetch(1)
        if item_set:
            result = item_set[0].description
            memcache.add(itemcode, result, namespace='codelookup-description')
        else:
            result = '**unknown**'
    return result
