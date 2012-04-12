from random import sample
# http://sourceforge.net/projects/pydes/
from pyDes import des, triple_des, PAD_PKCS5
# http://ivoras.sharanet.org/projects/blowfish.html
from blowfish import Blowfish

class Crypto(object):
    backend = None # Encriptor class
    key = None # Encription key
    algorithm = None # Encryption algorithm name
    
    __key_chars = ( '\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b' +
                    '\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16' +
                    '\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%' +
                    '&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMN' +
                    'OPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvw' +
                    'xyz{|}~\x7f' ) # ASCII CHARS
    __key_chars = ( 'abcdefghijklmnopqrstuvwxyz123456789' )
        
    __key_length = {
        "des":8,
        "3des":24, # 24 or 16
        "blowfish":56, # 8 to 56
        }
            
    def __genkey__(self, a):
        l = self.__key_length[a]
        return "".join( sample( self.__key_chars*l, l ))
        
    def __blowfishEncrypt__(self, c):
        self.backend.initCTR()
        return self.backend.encryptCTR(c)
        
    def __blowfishDecrypt__(self, c):
        self.backend.initCTR()
        return self.backend.decryptCTR(c)
        
    def __init__(self, key = None, backend = "3des"):
        backend = backend.lower()
        if backend == "des":
            key = key or self.__genkey__("des")
            self.backend = des( key, padmode=PAD_PKCS5 )
            self.encrypt = self.backend.encrypt
            self.decrypt = self.backend.decrypt
            self.key = key
            self.algorithm = backend
        elif backend in ("3des","trides","triple_des"):
            key = key or self.__genkey__("3des")
            self.backend = triple_des( key, padmode=PAD_PKCS5 )
            self.encrypt = self.backend.encrypt
            self.decrypt = self.backend.decrypt
            self.key = key
            self.algorithm = backend
        elif backend == "blowfish":
            key = key or self.__genkey__("blowfish")
            self.backend = Blowfish(key)
            self.encrypt = self.__blowfishEncrypt__
            self.decrypt = self.__blowfishDecrypt__
            self.key = key
            self.algorithm = backend

if __name__ == "__main__":
    from time import time
    import string
    results = []
    byte = "a"
    test = {
        #"des":"DES' key", #Because is insecure
        "3des":"This is the tri-DES key.",
        "blowfish":"This is the blowfish key",
        }
    times = 5
    for k in xrange(3,15):
        text = byte*(2**k)
        for i in test.keys():
            r = True
            it = 0
            ct = 0
            et = 0
            for j in xrange(times):
                init0 = time()
                o = Crypto(key=test[i],backend=i)
                init1 = time()
                c0 = time()
                c = o.encrypt( text )
                c1 = time()
                e0 = time()
                e = o.decrypt( c )
                e1 = time()
                r = r and (e == text)
                it += (init1-init0)/times
                ct += (c1-c0)/times
                et += (e1-e0)/times
            
            results.append({
                "type":i,
                "total":it+ct+et,
                "init":it,
                "encrypt":ct,
                "decrypt":et,
                "success":r
                })
        better = None
        bettertime = 0
        for i in results:
            '''
            print ("Algorithm name      : %(type)s\n" +
                    "Initialization time : %(init)s\n" +
                    "Encryption time     : %(encrypt)s\n" +
                    "Decrypting time     : %(decrypt)s\n" +
                    "Total               : %(total)s\n" +
                    "Sucess              : %(success)s\n") % i'''
            if not better or i["total"] < bettertime:
                better = i["type"]
                bettertime = i["total"]
        print "For %d bytes, the better is %s" % (2**k, better)
    
        
