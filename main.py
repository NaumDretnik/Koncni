#!/usr/bin/env python
import os
import jinja2
import webapp2
import cgi
import json
from google.appengine.api import urlfetch
from google.appengine.api import users

from models import Message


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


def user_main():
    user = users.get_current_user()
    if user:
        logged_in = True
        logout_url = users.create_logout_url("/")

        url = "http://api.openweathermap.org/data/2.5/weather?q=Ljubljana&APPID=bd1a3e93fca9eb0e64b5c9b17bc9bcc3"
        data = urlfetch.fetch(url).content
        json_data = json.loads(data)

        temp_kelvin = float(json_data["main"]["temp"])
        temp_c = str(temp_kelvin - 273.15)
        main = json_data["weather"][0]["description"]

        messages = Message.query(Message.recipient == user.email()).order(-Message.timestamp).fetch()
        messages_sent = Message.query(Message.sender == user.email()).order(-Message.timestamp).fetch()

        params = {
            "user": user,
            "logged_in": logged_in,
            "logout_url": logout_url,
            "temp_c": temp_c,
            "main": main,
            "messages": messages,
            "messages_sent": messages_sent,
        }
    else:
        logged_in = False
        login_url = users.create_login_url("/")
        params = {
            "user": user,
            "logged_in": logged_in,
            "login_url": login_url,
        }
    return params


class MainHandler(BaseHandler):
    def get(self):
        params = user_main()
        return self.render_template("index.html", params)


class MessageHandler(BaseHandler):
    def get(self):
        params = user_main()
        return self.render_template("new_message.html", params)

    def post(self):
        sender = cgi.escape(self.request.get("sender"))
        recipient = cgi.escape(self.request.get("recipient"))
        subject = cgi.escape(self.request.get("subject"))
        content = cgi.escape(self.request.get("content"))
        msg_save = Message(sender=sender, recipient=recipient, subject=subject, content=content)
        msg_save.put()
        return self.redirect("/")


class SentMessagesHandler(BaseHandler):
    def get(self):
        params = user_main()
        return self.render_template("sent.html", params)


app = webapp2.WSGIApplication([
        webapp2.Route('/', MainHandler),
        webapp2.Route('/new_message', MessageHandler),
        webapp2.Route('/sent_messages', SentMessagesHandler),

], debug=True)
