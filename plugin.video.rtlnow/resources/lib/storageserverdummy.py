# -*- coding: utf-8 -*-

'''
     StorageServer override
     Version: 1.0
    Copyright (C) 2010-2011 Tobias Ussing And Henrik Mosgaard Jensen
    Copyright (C) 2019 anxdpanic
'''

class StorageServer(object):
    def __init__(self, table, timeout=24):
        pass

    def cacheFunction(self, funct=False, *args):
        if funct:
            return funct(*args)
        return []

    def set(self, name, data):
        return ""

    def get(self, name):
        return ""

    def delete(self, name):
        return ""

    def setMulti(self, name, data):
        return ""

    def getMulti(self, name, items):
        return ""

    def lock(self, name):
        return False

    def unlock(self, name):
        return False