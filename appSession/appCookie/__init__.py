from Cookie26 import BaseCookie
class Cookie(BaseCookie):
    ''' BaseCookie wrapper '''
    def append(self, key, value, HttpOnly = False,
    httponly = False, max_age = None, path = None, domain = None,
    secure = None, version = None, comment = None):
        ''' Simple interface to add a cookie '''
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
                
    def toString(self):
        return self.output()
