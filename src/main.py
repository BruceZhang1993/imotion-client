#!/usr/bin/env python3
#-- coding: utf-8 --

import sys, os, logging, errno

from PyQt5.QtWidgets import QMainWindow, QApplication

from src.database import Database
import src.functions

HOMEDIR = os.environ['HOME']
APPDIR = HOMEDIR + "/.imotion"
DEBUG = True

class ImotionMain(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        pass

def _firstrun():
    logger.debug("Creating APPDIR...")
    src.functions.create_dir(APPDIR)

def _setlogfile():
    logger.debug('Enabling file logging...')
    fh = logging.FileHandler(APPDIR + '/imotion.log')
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    logger.info('File logging has been started.')

def _initlogger():
    logger = logging.getLogger('imotion')
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    if DEBUG:
        sh.setLevel(logging.DEBUG)
    logger.addHandler(sh)
    return logger

if __name__ == '__main__':
    logger = _initlogger()
    try:
        _firstrun()
        _setlogfile()
    except OSError as e:
        logger.warning("OSError: %s" % e)
    # Init database at startup.
    Database()
    imotionapp = QApplication(sys.argv)
    imotionmain = ImotionMain()
    imotionmain.show()
    sys.exit(imotionapp.exec_())