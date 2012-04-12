# -*- coding: utf-8 -*-
''' Python AppEngine Sessions %(__version__)
    %(__author__)
    %(__authemail__)

    Licensed under General Public License version 3 Terms:

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

'''
    Usage:
    You need to initialize a Session object, on every request, giving
    the current RequestHandler instance for proper Cookie handling.
    Session instance's write method must be invoked before request
    finished and data was send to client.
    
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
        * __getitem__ and __setitem__
            Methods for dictionary like behavior. You can access sesion
            data directly, prefixing underscore ("_") for server data
            on keys' names.
        * write
            This metod must be invoked before request's ending to save
            session cookies on http headers. 
'''

__all__ = ["DataDict","Session"]
__author__ = "Felipe A. Hernandez"
__authemail__ = "spayder26 at gmail dot com"
__version__ = "0.1"
__license__ = "GPLv3"

import logging
from google.appengine.api import memcache
from base64 import b64encode as encode, b64decode as decode
from random import sample

from PRSerializer import dumps as dump, loads as load, register as serializable

from appCookie import Cookie as SessionCookie
from appCrypto import Crypto as Encryptor
      
class DataDict(dict):
    # A dictionary with a public ischanged flag,
    # without KeyErrors (return None if key not found),
    # and items will be removed if None is asigned
    changed = False
    def __getstate__(self):
        return dict(self) # Pickles as dict
        
    def __setstate__(self, d):
        return self.__init__(d)
    
    def __getitem__(self, key):
        if dict.__contains__(self, key):
            return dict.__getitem__(self, key)
        return None
    
    def __setitem__(self, key, value):
        if value == None:
            self.__delitem__(key)
        else:
            dict.__setitem__(self, key, value)
            self.changed = True
        
    def __delitem__(self, key):
        if dict.__contains__(self, key):
            dict.__delitem__(self, key)
            self.changed = True
serializable(DataDict)

class Session(object):
    # Session class, required to be initialized with a request handler
    # and write() method must be exec before sending content to client  
    
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
    __cookie_sid  = "oeditor-session"
    __cookie_data = "oeditor-session-data"
    
    # Memcache namespace
    __memcache_namespace = "oeditor-session"
    
    # Convenience request and response instances
    request = None
    response = None
    
    def __gensid__(self, length = None):
        ''' Generates the session ID '''
        if not length:
            length = self.__sid_length
        return "".join( sample( self.__sid_chars*length, length) )
        
    def __encrypt__(self, dict, serialize=False):
        ''' encrypt session-data, pickles if serialized '''
        if serialize:
            return encode( self.__crypt.encrypt( dump( dict , -1 ) ) )
        return encode( self.__crypt.encrypt( dict ) )
        
    def __decrypt__(self, string, serialize=False):
        ''' Decrypt session-data, pickles if serialized '''
        try:
            if serialize:
                return load( self.__crypt.decrypt( decode( string ) ) )
            else:
                return self.__crypt.decrypt( decode( string ) )
        except UnpicklingError:
            return None
            
    def __memget__( self, sid, namespace = None ):
        if isinstance(sid, list):
            pass
        return memcache.get(
            sid,
            namespace=(
                namespace or self.__memcache_namespace
                )
            )
        
    def __memset__(self, sid, data=None, namespace = None):
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
    
    def __init__(self, requestHandler, time = 3600, path = None):
        # Session initialization, reads from request cookies and looks
        # for session cookies. Then, theyre are decrypted and validated
        # against memcache.

        self.__clientvars = DataDict()
        self.__servervars = DataDict()
        self.__path = path or "/"
        self.__memtime = time
        
        self.request = requestHandler.request
        self.response = requestHandler.response
        
        cookies = SessionCookie( self.request.headers.get('Cookie') )  
        if (self.__cookie_sid in cookies) and  \
           (self.__cookie_data in cookies):
            # Cookies
            c = cookies[ self.__cookie_sid ]
            d = cookies[ self.__cookie_data ]

            # Requesting server-side session data
            sdata = self.__memget__( c.value )
            if isinstance(sdata, DataDict):
                # New encryptor with server key
                #try:
                self.__crypt = Encryptor( sdata["key"], sdata["encryption"] )
                # Decrypting the cookie data
                cdata = self.__decrypt__( d.value , serialize = True )
                if isinstance(cdata, DataDict):
                    logging.info("Session id: %s" % repr(c.value) )
                    logging.info("Client data: %s" % repr(cdata) )
                    logging.info("Server data: %s" % repr(sdata) )
                    # TODO: Validating cookie data

                    # If everything is correct, we accept the data
                    self.__sid = c.value
                    self.__clientvars = cdata
                    self.__servervars = sdata
                '''except:
                    # Ban behavior
                    pass'''

        if self.__sid == None:
            logging.info("no cookie")
            self.__isnew = True
            self.__sid = self.__gensid__()  # New session id
            self.__crypt = Encryptor() # New encryptor
            self.__servervars["key"] = self.__crypt.key # Save key on server
            self.__servervars["encryption"] = self.__crypt.algorithm # Remember algorithm
            
    # Dict-like methods
    def __setitem__(self, key, value):
        if key[0]=="_":
            self.__servervars.__setitem__(key, value)
        else:
            self.__clientvars.__setitem__(key, value)
        
    def __getitem__(self, key):
        if key[0]=="_":
            return self.__servervars.__getitem__(key)
        return self.__clientvars.__getitem__(key)
    
    def __contains__(self, key):
        if key[0]=="_":
            return self.__servervars.__contains__(key)
        return self.__clientvars.__contains__(key)
    
    # Public
    def write(self):
        # Writes session cookies on response object's headers
        if self.__servervars.changed:
            # Server side data
            self.__memset__( self.__sid, self.__servervars )
    
        # We create an up-to-date SessionCookie from request headers
        cookies = SessionCookie( self.request.headers.get('Cookie') )
        
        if self.__isnew:
            #logging.info("setted %s" % self.__cookie_sid)
            # Client side session id
            cookies.append(
                self.__cookie_sid,
                self.__sid,
                HttpOnly = True,
                path = self.__path,
                )
        
        if self.__isnew or self.__clientvars.changed:
            #logging.info("setted %s" % self.__cookie_data)
            # Client side data
            cookies.append(
                self.__cookie_data,
                self.__encrypt__(self.__clientvars , serialize = True),
                HttpOnly = True,
                path = self.__path,
                )    
        
        self.response.headers['Set-cookie'] = cookies.toString()
