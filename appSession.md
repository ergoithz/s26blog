Note this documentation can be outdated, but starting on 1.2 appSession version it supports pydoc.

If you are using linux you can generate documentation:
```
export PYTHONPATH=YOUR_APPENGINE_SDK_DIRECTORY
cd appSession_directory
pydoc -w appSession
```

# Introduction #

Due Google App Engine API doesn't provide a Session variables management system, and due I don't like some implementations I've seen, I've implemented my own one.
This module uses [PRSerializer](PRSerializer.md), appCookie (a wrapper around [Python 2.6's Cookie module](http://docs.python.org/library/cookie.html)) and appCrypto (a wrapper for Todd Whiteman's PyDes and Michael Gilfix's blowfish. Both are encryption algorithms).

This module allows you to identify uniquely user browsers using a session id cookie, and store all data you want safely on server (using memcache), and safe-less on client browsers onto another encrypted serialized cookie.

I've used for user's logging and session on some of my projects, so it's slightly tested.

# Usage #
**You need to initialize a Session object, on every request**, giving the current RequestHandler instance for proper Cookie handling.
Session instance's write method must be invoked before request finished and data was send to client.

## Classes ##
  * `DataDict`
> > Inherits of Python Dictionary.
> > A simple serializable dictionary without KeyErrors. It returns None when key was not found). It has also a flag (changed), which is setted to true when a item is setted. If you modify an inner object, you must set "changed" flag to true manually.

  * `Session`
> > Abstraction layer for two DataDicts, one for server and another for a client, and Session-cookie and memcache interface.
> > It's dictionary-like, keys prefixed with an underscore (`_`) will be stored on server, anyelse will be encrypted and stored on client's browser as a cookie.
> > So be carefull storing sensible data on client.
    * Methods:
      * `__init__( requestHandler object [, int time, str path ] )`
> > > > Class constructor (automatically called when instancing class).
        * requestHandler object
> > > > > It's `self` in your RequestHandler class when using Google App Engine API.
        * int time
> > > > > Memcache key expiration time, either relative number of seconds from current time (up to 1 month), or an absolute Unix epoch time. 0 means forever.
        * str path
> > > > > Base path for cookies, it None or nothing given, "/" will be used.
      * `__getitem__( str key )` and `__setitem__( str key, object value )`

> > > > Methods for dictionary like behavior. You can access sesion data directly, prefixing underscore (`_`) for server data on keys' names.
      * `write( )`
> > > > This method must be invoked before request's ending to save session cookies on http headers and memcache updates.

## Example ##

A simple page which remember how many times user visited a page, and stores strings on server and client's cookies.
```
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import webapp
from appSession import Session

class RequestWeb(webapp.RequestHandler):
    def get(self):
        session = Session(self)
        if session["visited"]:
            text = "Times visited %d." % session["visited"]
            session["visited"] += 1
        else:
            text = "First time on page."
            session["visited"] = 1
                
        session["_foo"] = "This string will be stored on server."
        session["bar"] = "This string will be stored on a cookie."
    
        session.write()
        self.response.out.write(
            "<html><head></head><body><p>%s</p></body></html>" % text
            )

application = webapp.WSGIApplication([
    ('/',RequestWeb)
    ],
    debug=True)

run_wsgi_app(application)
```