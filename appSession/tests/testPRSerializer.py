#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import os.path
import doctest
import pickle
import cPickle
import pprint
import timeit
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import PRSerializer

from PRSerializer import Serializer
from oldPRSerializer import Serializer as OldSerializer, register as old_serializable

class OldStyleTestClass:
    def __init__(self, a=None, b=None):
        self.a = a
        self.b = b

    def __getstate__(self):
        return (self.a, self.b)

    def __setstate__(self, data):
        self.a, self.b = data

class NewStyleTestClass(object):
    def __init__(self, a=None, b=None):
        self.a = a
        self.b = b

    def __getstate__(self):
        return (self.a, self.b)

    def __setstate__(self, data):
        self.a, self.b = data

class CustomConstructorTestClass(object):
    def __init__(self, a=None, b=None):
        self.a = a
        self.b = b

    def __getstate__(self):
        return (self.a, self.b)

    @classmethod
    def __setstate__(cls, data):
        return cls(*data)

def format_results(result_dict):
    return pprint.pformat(result_dict)

def legacy_compatibility():
    Serializer.compression = 1
    legacy = OldSerializer.dumps({"a":{"b":1},(1,1):2})
    new = Serializer.dumps({"a":{"b":1},(1,1):2})
    r = [
        ("Legacy", legacy, Serializer.loads(legacy)),
        ("New", new, Serializer.loads(new))
        ]
    return r

def new_vs_legacy():
    n = 500
    d = {i:i+1 for i in xrange(100)}
    od = OldSerializer.dumps(d)
    nd = Serializer.dumps(d)
    r = [
        ("Serializing dict (new vs old)",
            timeit.timeit(lambda: Serializer.dumps(d), number=n),
            timeit.timeit(lambda: OldSerializer.dumps(d), number=n),
            ),
        ("Unserializing old format (new vs old)",
            timeit.timeit(lambda: Serializer.loads(od), number=n),
            timeit.timeit(lambda: OldSerializer.loads(od), number=n),
            ),
        ("Unserializing new format (new only)",
            timeit.timeit(lambda: Serializer.loads(nd), number=n),
            )
        ]
    return r

def new_vs_pickle():

    times = 10000
    # Old registration
    old_serializable(OldStyleTestClass)
    old_serializable(NewStyleTestClass)
    old_serializable(CustomConstructorTestClass)

    # New registration
    Serializer.serializable(OldStyleTestClass)
    Serializer.serializable(NewStyleTestClass)
    Serializer.serializable(CustomConstructorTestClass)

    p = [testClass(1,2) for testClass in (OldStyleTestClass, NewStyleTestClass, CustomConstructorTestClass)]
    
    r = []
    for c in p:
        Serializer.compression = 9
        compressed_time = timeit.timeit(lambda: Serializer.dumps(c), number=times)
        Serializer.compression = 0
        r.append(
            ("%s object" % c.__class__.__name__, (
                ("Pickle", timeit.timeit(lambda: pickle.dumps(c), number=times)),
                ("cPickle", timeit.timeit(lambda: cPickle.dumps(c), number=times)),
                ("Serializer", timeit.timeit(lambda: Serializer.dumps(c), number=times)),
                ("Serializer compressed", compressed_time)
                )))
    p.append({i:(0,1,3,4,5,6,7,8,9) for i in xrange(10000)})

    times = 10
    c = p
    Serializer.compression = 9
    compressed_time = timeit.timeit(lambda: Serializer.dumps(c), number=times)
    Serializer.compression = 0
    r.append(
        ("Mixed data", (
            ("Pickle", timeit.timeit(lambda: pickle.dumps(c), number=times)),
            ("cPickle", timeit.timeit(lambda: cPickle.dumps(c), number=times)),
            ("Serializer", timeit.timeit(lambda: Serializer.dumps(c), number=times)),
            ("Serializer compressed", compressed_time)
            )))

    pickled = cPickle.dumps(p)
    Serializer.compression = 9
    compressed = Serializer.dumps(p)
    Serializer.compression = 0
    uncompressed = Serializer.dumps(p)
    
    r.append(
        ("Dump size in bytes", (
            ("cPickle", len(pickled)),
            ("Serializer", len(uncompressed)),
            ("Serializer compressed", len(compressed))
            )))
    r.append(
        ("Mixed data unpickling", (
            ("Pickle", timeit.timeit(lambda: pickle.loads(pickled), number=times)),
            ("cPickle", timeit.timeit(lambda: cPickle.loads(pickled), number=times)),
            ("Serializer", timeit.timeit(lambda: Serializer.loads(uncompressed), number=times)),
            ("Serializer compressed",  timeit.timeit(lambda: Serializer.loads(compressed), number=times))
            )))
    
    return r

if __name__ == "__main__":
    #for test in (legacy_compatibility, new_vs_legacy, new_vs_pickle):
    #    print format_results(test())

    Serializer.compression = 0
    print doctest.testmod(PRSerializer)
