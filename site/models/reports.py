import logging
from google.appengine.ext import db
from google.appengine.api import users

from exceptions import Exception


class ReportError(Exception):
    pass


class Report(db.Model):
    """ Association betw User and Role
    """
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    name = db.StringProperty(verbose_name="Report Name")
    instance = db.DateTimeProperty(verbose_name="Instance Id")
    rowNumber = db.IntegerProperty(verbose_name="Row Number")
    rowText = db.StringProperty(verbose_name="Row Text")


