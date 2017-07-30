#!/usr/bin/env python3
#-- coding: utf-8 --

import sqlite3
import threading, os, logging

import imotion.functions as functions

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

    name = None
    # Default database located in RAM.
    def __init__(self, name='default'):
        if self.name:
            self._del()
        if name.lower() == 'default':
            logger.debug('Creating database `default` in RAM...')
            # src.functions.create_dir(DBDIR)
            self.default = sqlite3.connect(':memory:')
            self.cursor = self.default.cursor()
            logger.info('Database `default` in RAM has been created successfully.')
        else:
            dbfile = "%s/%s.db" % (DBDIR, name)
            logger.debug('Creating database `%s` at `%s` ...' % (name, dbfile))
            functions.create_dir(DBDIR)
            eval("self.%s = sqlite3.connect('%s')" % (name, dbfile))
            self.cursor = eval("self.%s.cursor()" % name)
            logger.info("Database `%s` at `%s` has been created successfully." % (name, dbfile))

    def _del(self):
        self.cursor.close()
        eval("self.%s.close()" % self.name)

    def __del__(self):
        self._del()
