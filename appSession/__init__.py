# -*- coding: utf-8 -*-
''' 
Google App Engine Session, appSession 0.1.3
Felipe A. Hernandez
spayder26 at gmail dot com

License:
    This library is licensed under LGPLv3.
    http://www.gnu.org/licenses/lgpl-3.0.html

Introduction:
    There are some session managers for Google App Engine, but when I
    started they simply didn't exits, so I wrote this, taking special
    care of security and pickling-unpickling data performance.
    
    Security:
    * PRSerializer only unpickles known objects (aka. registered
      classtypes), avoiding python Pickle/cPickle unsafety.
    * Data cookie is encrypted using 3des algorithm using an randomly
      generated 24 bytes-length passphrase, which is regenerates on any
      cookie change. That means that hackers have to break every cookie
      encryption separately, and it avoids 3des algorithm collisions.
    * A cookie checksum is stored along with session id and passprase on
      server, avoiding any changes by anyone which would decrypt the
      cookie.
      
    Performance:
    * PRserializer is fast as Pickle (its faster on serializing and a
      bit slower on unserialzing).
    * The 3des encryption algorithm is the faster safe one I've found.
      PyCrypto backend will be used if available or pyDes, a pure python
      implementation, will be loaded.
    * Data is written on Request and memcache once, and only once, per
      request (when Session.write method is called).

Usage:
    You need to initialize a Session object, on every request, giving
    the current RequestHandler instance for proper Cookie handling.
    Session instance's write method must be invoked before request
    finished and data was send to client.

    Important:
        "~key", "~hash" and "~method" server items are reserved because
        they're used internally by the Session object, so do not modify
        them unless you know exactly what are you doing.

Classes:
    * DataDict:
        A simple serializable dictionary without KeyErrors. It returns
        None when key was not found). It has also a flag (changed),
        which is setted to true when a item is setted. If you modify
        an inner object, you must set "changed" flag to true manually.
        
    * Session:
        Abstraction layer for two DataDicts, one for server and another
        for a client, and Session-cookie interface.
        It's dictionary-like, keys prefixed with an underscore ("_")
        will be stored on server, anyelse will be encrypted and stored
        on client's browser as a cookie.
        So be carefull storing sensible data on client.
        Methods:
        * write
            This metod must be invoked before request's ending to save
            session cookies on http headers and memcache data.
        Properties:
        * `client`
            dict-like object whose items will be stored on the extremely
            safe client's cookie.
        * `server`
            didct-like object whose items will be stored in server's
            memcache.
    
        
Example:
    import webapp2
    from appSession import Session, serializable
    
    @serializable # Python 2.6+, same as serializable(MyClass)
    class MyClass(object):
        def __init__(self):
            self.foo = 0
            
        def __getstate__(self):
            return (self.foo,)
            
        def __setstate__(self, o):
            self.foo = o[0]

    class RequestWeb(webapp2.RequestHandler):
        def get(self, asdf=None):
            # Let's create our Session object for this request
            session = Session(self, debug=True) 
            
            # Per-user visit counter stored on a cookie
            if session.client["visited"]:
                text = "Times visited %d." % session.client["visited"]
                session.client["visited"] += 1
            else:
                text = "First time on page."
                session.client["visited"] = 1
                    
            session.server["foo"] = "This string will be stored on server."
            session.client["bar"] = "This string will be stored on a cookie."
            
            # We can also store Python objects thanks to PRSerializer
            if session.server["instance"] == None:
                session.server["instance"] = MyClass()
            session.server["instance"].foo += 1
            
            session.write() # At last, we need to write session data.
            self.response.out.write(
                "<html><head></head><body><p>%s</p></body></html>" % text
                )

    app = webapp2.WSGIApplication((
        (r'/', RequestWeb),
        ), debug=True)

'''

__all__ = ("DataDict","Session", "serializable")
__author__ = "Felipe A. Hernandez"
__authemail__ = "spayder26 at gmail dot com"
__version__ = "0.1.3"
__license__ = "LGPLv3"

import logging
from google.appengine.api import memcache
from base64 import b64encode as encode, b64decode as decode
from random import sample
from hashlib import md5

from PRSerializer import dumps as dump, loads as load, serializable

from appCrypto import Crypto as Encryptor

from sys import version_info as python_version
if python_version < (2,6): from Cookie26 import BaseCookie
else: from Cookie import BaseCookie

class SessionCookie(BaseCookie):
    '''BaseCookie wrapper'''
    def append(self, key, value, HttpOnly = False,
    httponly = False, max_age = None, path = None, domain = None,
    secure = None, version = None, comment = None):
        '''Simple interface to add a cookie.'''
        self.__setitem__(key, value)
        if max_age is not None:
            self.__getitem__(key).__setitem__('expires', str(max_age))  
        for var_name, var_value in [
            ('max-age', max_age),
            ('path', path),
            ('domain', domain),
            ('secure', secure),
            ('HttpOnly', HttpOnly or httponly), # Only available on 2.6
            ('version', version),
            ('comment', comment),
            ]:
            if not var_value in (None, False):
                self.__getitem__(key).__setitem__(var_name, str(var_value))

    def __str__(self):
        return "<SessionCookie %s>" % repr(self.output())
      
class DataDict(dict):
    '''A dictionary with a public 'changed' boolean flag, without
    KeyErrors (return None if key not found) and items will be removed
    if None is asigned, serializable by PRSerializer.
    '''
    
    _changed = False
    @property
    def changed(self):
        return self._changed
    
    def __getstate__(self):
        return dict(self) # Pickles as dict
        
    def __setstate__(self, d):
        '''Serialization set method. See `PRSerializer`.'''
        return self.__init__(d)
    
    def __getitem__(self, key):
        '''Serialization get method. See `PRSerializer`.'''
        if dict.__contains__(self, key):
            return dict.__getitem__(self, key)
        return None
    
    def __setitem__(self, key, value):
        '''x.__setitem__(i, y) <==> x[i]=y'''
        if value == None:
            self.__delitem__(key)
        else:
            dict.__setitem__(self, key, value)
            self._changed = True
        
    def __delitem__(self, key):
        '''x.__getitem__(y) <==> x[y]'''
        if dict.__contains__(self, key):
            dict.__delitem__(self, key)
            self._changed = True

serializable(DataDict)

class Session(object):
    '''Session class, required to be initialized with a request handler
    and write() method must be exec before sending content to client'''
    
    # Session data
    __crypt = None # Initialized cryptographic class
    __sid = None # Session id
    __isnew = False # If session was created on this request
    __clientvars = None # Client data dictionary
    __servervars = None # Server data dictionary
    
    # Sid generator settings
    __sid_length = 64
    __sid_chars = ('0123456789' +
                   'ABCDEFGHIJKLMNOPQRSTUVWXYZ' +
                   'abcdefghijklmnopqrstuvwxyz' +
                   "!#$%&'*+-.^_`|~")
    __sid_chars_length = len(__sid_chars)
    
    # Cookies config
    __cookie_sid  = "-session"
    __cookie_data = "-session-data"
    
    # Server config
    __server_key    = "~key"
    __server_method = "~method"
    __server_hash   = "~hash" 
    __memcache_namespace = "-session"
    
    # Convenience request and response instances
    request = None
    response = None
    
    @property
    def server(self): return self.__servervars
    
    @property
    def client(self): return self.__clientvars
    
    def __gensid__(self, length = None):
        ''' Generates the session ID
        
        Arguments:
            length: the length of the generated id
        
        Return:
            Random id with given length.'''
        if not length:
            length = self.__sid_length
        return "".join( sample( self.__sid_chars*length, length) )
        
    def __encrypt__(self, data):
        '''Serialize and encrypt object.
        
        Arguments:
            data: object will be serialized and encrypted.
            
        Returns:
            Encrypted serialized string.
        '''
        return encode( self.__crypt.encrypt( dump( data , -1 ) ) )
        
    def __decrypt__(self, data):
        '''Decrypt and unserialize object
        
        Arguments:
            data: str object of encrypted serialized data
            
        Returns:
            Unserialized object.'''
        try:
            return load( self.__crypt.decrypt( decode( data ) ) )
        except UnpicklingError:
            return None
            
    def __memget__( self, sid, namespace = None ):
        '''Serialization get method. See `PRSerializer`.'''
        if isinstance(sid, list): pass
        return memcache.get(
            sid,
            namespace=(
                namespace or self.__memcache_namespace
                )
            )
        
    def __memset__(self, sid, data=None, namespace = None):
        '''Serialization set method. See `PRSerializer`.'''
        if isinstance(sid, dict):
            pass
        elif data:
            memcache.set(
                sid,
                data,
                namespace=(
                    namespace or self.__memcache_namespace
                    ),
                time=self.__memtime,
                )
    
    def __init__(self, requestHandler, time = 3600, path = "/", cookie_prefix = "app", debug = False):
        '''Session initialization, reads from request cookies and looks
        for session cookies. Then, theyre are decrypted and validated
        against memcache.
        
        This object supports key indexing (__getitem__ and __setitem__)
        and the *in* operator.
        
        Arguments:
            requestHandler: Appengine or wsgi compatible handler
                            instance.
            time: Memcache data expiration time. Defaults to 3600.
            path: Cookie domain path. Defaults to "/".
            cookie_prefix: string will be used prefixing cookie names.
                           Defaults to "app".
            debug: print logging messages on write. Defaults to False.

        '''
        self.__clientvars = DataDict()
        self.__servervars = DataDict()
        self.__path = path
        self.__memtime = time
        self.__cookie_prefix = cookie_prefix
        
        self.debug = debug
        self.request = requestHandler.request
        self.response = requestHandler.response
        
        cookiesid = "%s%s" % (cookie_prefix, self.__cookie_sid)
        cookiedata = "%s%s" % (cookie_prefix, self.__cookie_data)
        
        cookies = SessionCookie( self.request.headers.get('Cookie') )  
        if (cookiesid in cookies) and (cookiedata in cookies):
            # Cookies
            c = cookies[ cookiesid ]
            d = cookies[ cookiedata ]

            # Requesting server-side session data
            sdata = self.__memget__( c.value )
            # Validating server data and hash against cookie
            if isinstance(sdata, DataDict) and sdata[self.__server_hash] == md5(d.value).hexdigest():
                # New encryptor with server key
                self.__crypt = Encryptor( sdata[self.__server_key], sdata[self.__server_method] )
                # Decrypting the cookie data
                cdata = self.__decrypt__( d.value )
                # Validating cookie data
                if isinstance(cdata, DataDict):
                    if self.debug:
                        logging.info("Session id: %s" % repr(c.value) )
                        logging.info("Client data: %s" % repr(cdata) )
                        logging.info("Server data: %s" % repr(sdata) )

                    # If everything is correct, we accept the data
                    self.__sid = c.value
                    self.__clientvars = cdata
                    self.__servervars = sdata

        if self.__sid == None:
            logging.info("no cookie")
            self.__isnew = True
            self.__sid = self.__gensid__()  # New session id
            self.__crypt = Encryptor() # New encryptor
            self.__servervars[self.__server_key] = self.__crypt.key # Save key on server
            self.__servervars[self.__server_method] = self.__crypt.algorithm # Remember algorithm
            
    def __setitem__(self, key, value):
        '''Deprecated since 0.1.3: x.__setitem__(i, y) <==> x[i]=y'''
        logging.warn("Session.__setitem__ is deprecated since 0.1.3, use `server` and `client` dict-like objects instead.")
        if key[0]=="_": self.__servervars[key[1:]] = value
        else: self.__clientvars[key] = value
        
    def __getitem__(self, key):
        '''Deprecated since 0.1.3: x.__getitem__(y) <==> x[y]'''
        logging.warn("Session.__getitem__ is deprecated since 0.1.3, use `server` and `client` dict-like objects instead.")
        if key[0]=="_": return self.__servervars[key[1:]]
        return self.__clientvars[key]
    
    def __contains__(self, key):
        '''Deprecated since 0.1.3: D.__contains__(k) -> True if D has a key k, else False'''
        logging.warn("Session.__contains__ is deprecated since 0.1.3, use `server` and `client` dict-like objects instead.")
        if key[0]=="_":
            return self.__servervars.__contains__(key[1:])
        return self.__clientvars.__contains__(key)
    
    def write(self):
        '''Writes session cookies on response object's headers.'''
    
        # We create an up-to-date SessionCookie from request headers
        cookies = SessionCookie() #self.request.headers.get('Cookie') )
        
         # Client side session id
        if self.__isnew:
            if self.debug: logging.info("setted %s%s" % (self.__cookie_prefix, self.__cookie_sid))
           
            cookies.append(
                "%s%s" % (self.__cookie_prefix, self.__cookie_sid),
                self.__sid,
                HttpOnly = True,
                path = self.__path,
                )
        # Client side data
        if self.__isnew or self.__clientvars.changed:
            if self.debug: logging.info("setted %s%s" % (self.__cookie_prefix, self.__cookie_data))
            data = self.__encrypt__(self.__clientvars)
            self.__servervars[self.__server_hash] = md5(data).hexdigest()
            cookies.append(
                "%s%s" % (self.__cookie_prefix, self.__cookie_data),
                data,
                HttpOnly = True,
                path = self.__path,
                )
        # Server side data 
        if self.__servervars.changed:
            self.__memset__( self.__sid, self.__servervars )

        for morsel in cookies.values():
            self.response.headers.add_header('Set-Cookie', morsel.OutputString(None))
