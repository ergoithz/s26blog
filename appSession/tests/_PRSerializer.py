#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, os.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PRSerializer import Serializer
from _old_PRSerializer import Serializer as OldSerializer

def legacy_compatibility():
    legacy = OldSerializer.dumps({"a":{"b":1},(1,1):2})
    print "Legacy", repr(legacy), Serializer.loads(legacy)
    new = Serializer.dumps({"a":{"b":1},(1,1):2})
    print "New", repr(new), Serializer.loads(new)

def new_vs_legacy():
    import timeit
    n = 500
    d = {i:i+1 for i in xrange(1000)}
    print timeit.timeit(lambda: Serializer.dumps(d),number=n), timeit.timeit(lambda: OldSerializer.dumps(d),number=n)
    d = OldSerializer.dumps(d)
    print timeit.timeit(lambda: Serializer.loads(d),number=n), timeit.timeit(lambda: OldSerializer.loads(d),number=n)
    d = Serializer.dumps(d)
    print timeit.timeit(lambda: Serializer.loads(d),number=n)

if True:
    from time import time
    from string import ascii_letters, digits
    from pickle import dumps as pdumps, loads as ploads
    from zlib import compress, decompress
    from PRSerializer import serializable
    class DictInherited(dict):
        ''' This class inherits from dict, if not registered will be
            converted to dict when serializes '''
        pass

    @serializable("NewStyled") # Registering NewStyleClass, you can specify an alias if you want
    class NewStyleClass(object):
        ''' This class inherits from object, so it's a new-style class,
            it's __new__ method will be called (instead of __init__)
            before __setstate__ , when unserializes.

            Must be registered and it requires both __getstate__
            and __setstate__ methods for class registration.
            '''
        a = True
        b = False
        def __new__(self):
            ''' NewStyleClass __new__ will be called twice '''
            return object.__new__(self)
        def __init__(self):
            ''' NewStyleClass __init__ will be only called once '''
            pass
        def __getstate__(self):
            ''' Must return a serializable object which
                will be serialized '''
            return {"a":self.a,"b":self.b}
        def __setstate__(self, obj):
            ''' This method will handle unserialized data
                ( as returned by __getstate__ ) '''
            self.a = obj["a"]
            self.b = obj["b"]

    @serializable # Registering OldStyleClass
    class OldStyleClass:
        ''' This class is an old-style class, it's __init__ method will
            be called prior to it's __setstate__ method .
            Remember you can create an __new__ method by hand if you
            want to prevent __init__ will be called when unserializes.

            Must be registered and must have both __setstate__ and
            __getstate__ methods.
            '''
        def __init__(self):
            '''OldStyleClass __init__ will be called twice'''
            pass
        def __getstate__(self):
            return None
        def __setstate__(self,x):
            pass

    # Performance test
    a = DictInherited()
    loop0_range = xrange(1000)
    loop1_range = xrange(50)
    loop2_range = xrange(50)
    str1 = "a:a,a;0;a'''aa'" # for escape tests
    xra1 = xrange(1,100,2)
    for i in loop0_range:
        key = i
        a[key] = [str1,xra1,[]]
        for j in loop1_range:
            o = NewStyleClass()
            o.a = i < 500
            o.b = i > 499
            a[key].append(o)
        a[key].append(OldStyleClass())
        for j in loop2_range:
            a[key].append((True, False, ascii_letters+digits,i))

    
    
    print "Performance test: serializing, unserializing, zlib compression and pickle"
    print "  1 dict"
    print "    %d lists (%d are empty)" % (len(loop0_range)*2,len(loop0_range))
    print "      %d integers (%d are dictionary keys)" % (len(loop0_range)*len(loop2_range)*2,len(loop0_range))
    print "      %d strings" %(len(loop0_range)*len(loop1_range)+len(loop0_range)*len(loop2_range))
    print "      %d objects" %(len(loop0_range)*len(loop1_range)+len(loop0_range))
    print "      %d booleans" %(len(loop0_range)*len(loop2_range)*2)
    print
    
    t0 = time()
    b = Serializer.dumps(a)
    t1 = time()
    c = Serializer.loads(b)
    t2 = time()
    d = compress(b,9)
    t3 = time()
    
    print "Serializing time:   %fs ( %d bytes )" % (t1-t0,len(b))
    try:
        print "Unserializing time: %fs ( %2f B/s )" % (t2-t1, len(b)/(t2-t1))
    except ZeroDivisionError:
        print "Unserializing time: %fs ( %2f B/s )" % (t2-t1, len(b))
    print "Zlib compress time: %fs ( %d bytes )" % (t3-t2,len(d))
    t0 = time()
    b = pdumps(a,-1)
    t1 = time()
    c = ploads(b)
    t2 = time()
    d = compress(b,9)
    t3 = time()
    print
    print "Pickling time:      %fs ( %d bytes )" % (t1-t0,len(b))
    try:
        print "Unpickling time:    %fs ( %2f B/s )" % (t2-t1, len(b)/(t2-t1))
    except ZeroDivisionError:
        print "Unpickling time:    %fs ( %2f B/s )" % (t2-t1, len(b))
    print "Zlib compress time: %fs ( %d bytes )" % (t3-t2,len(d))

    print
    print "range vs xrange performance"
    r =  range(10000)
    x = xrange(10000)
    u = ["a%d" % i for i in x]
    l = [4,2,3,5]+range(len(r)-4)
    d = {"range(%d)" % len(r):r,"xrange(%d)" % len(x):x,"str list(%d)" % len(u):u,"unordered list2 (%d)" % len(l):l}
    for i, j in d.items():
        t0 = time()
        b = Serializer.dumps(j)
        t1 = time()
        c = Serializer.loads(b)
        t2 = time()
        print "%s : serializing %fs, unserializing %fs" % (i,t1-t0,t2-t1)

    Serializer.detect_range = False
    print "deactivating auto range detection"
    for i, j in d.items():
        t0 = time()
        b = Serializer.dumps(j)
        t1 = time()
        c = Serializer.loads(b)
        t2 = time()
        print "%s : serializing %fs, unserializing %fs" % (i,t1-t0,t2-t1)

    print
    print "range detection algorithm tests"
    def way1(x):
        if len(x)>1 and isinstance(x[0],int) and isinstance(x[1],int):
            last = x[1]
            step = last-x[0]
            e = True
            for i in x[2:]:
                if isinstance(i,int) and (last+step) == i:
                    last = i
                else:
                    e = False
                    return False
            return True
        return False

    def way2(x):
        if len(x)>1 and isinstance(x[0],int) and isinstance(x[1],int):
            step = x[1]-x[0]
            return x == range( x[0], x[-1] + step, step )
        return False

    l1 = range(10000)
    for i,j in (("way1",way1),("way2",way2)):
        t0 = time()
        o = j(l1)
        t1 = time()
        print i, o, (t1-t0), "seconds"

if __name__ == "__main__":
    #legacy_compatibility()
    #new_vs_legacy()
    #new_vs_pickle()
    pass
