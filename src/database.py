#!/usr/bin/env python3
#-- coding: utf-8 --

import sqlite3
import threading, os, logging

import src.functions

HOMEDIR = os.environ['HOME']
APPDIR = HOMEDIR + "/.imotion"
DBDIR = APPDIR + '/database'

logger = logging.getLogger('imotion')

class Singleton(object):

    objs = {}
    objs_locker = threading.Lock()

    def __new__(cls, *args, **kv):
        if cls in cls.objs:
            return cls.objs[cls]['obj']
        cls.objs_locker.acquire()
        try:
            if cls in cls.objs:  ## double check locking
                return cls.objs[cls]['obj']
            obj = object.__new__(cls)
            cls.objs[cls] = {'obj': obj, 'init': False}
            setattr(cls, '__init__', cls.decorate_init(cls.__init__))
        finally:
            cls.objs_locker.release()

    @classmethod
    def decorate_init(cls, fn):
        def init_wrap(*args):
            if not cls.objs[cls]['init']:
                fn(*args)
                cls.objs[cls]['init'] = True
            return
        return init_wrap

@Singleton
class Database(object):

    # Default database located in RAM.
    def __init__(self, name='default'):
        logger.debug('Creating database `default` in RAM...')
        src.functions.create_dir(DBDIR)
        eval("self.%s = sqlite3.connect(':memory:')" % name)
        logger.info('Database `default` in RAM has been created successfully.')

    def create(self, name):
        eval("self.%s = sqlite3.connect('%s/%s.db')" % (name, DBDIR, name))
        return eval("self.%s", name)