# -*- coding: utf-8 -*-

from google.appengine.ext import ndb


class Message(ndb.Model):
    content = ndb.StringProperty()
    subject = ndb.StringProperty()
    sender = ndb.StringProperty()
    recipient = ndb.StringProperty()
    timestamp = ndb.DateTimeProperty(auto_now_add=True)