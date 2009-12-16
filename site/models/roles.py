from datetime import datetime
import logging
from google.appengine.ext import db
from google.appengine.api import users

from exceptions import Exception



class RoleError(Exception):
    pass


class UserRole(db.Model):
    """ Association betw User and Role
    """
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    user = db.UserProperty(verbose_name="Domain Email")
    role = db.StringProperty(verbose_name='Role')

    @classmethod
    def hasRole(cls, user, role):
        roles = UserRole.all()
        logging.debug('hasRole: %s %s', user, role)
        roles.filter('user =', user)
        roles.filter('role =', role)
        return roles.get()



