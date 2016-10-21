#!/usr/bin/env python3
# -- coding: utf-8 --

import sys
import logging
# import errno

from PyQt5.QtWidgets import QApplication

# from database import Database
import functions
from const import *
from ui import ImotionMain


def _initlogger():
    logger = logging.getLogger("imotion")
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    logger.setLevel(logging.INFO)
    if DEBUG:
        logger.setLevel(logging.DEBUG)
    logger.addHandler(sh)
    return logger


def _firstrun():
    logger.debug("Creating APPDIR...")
    functions.create_dir(APPDIR)


def _setlogfile():
    logger.debug('Enabling file logging...')
    fh = logging.FileHandler(APPDIR + '/imotion.log')
    fh.setFormatter(logging.Formatter(
        '(%(asctime)s) [%(levelname)s] %(message)s'))
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    logger.info('File logging has been started.')


if __name__ == '__main__':
    logger = _initlogger()
    try:
        _firstrun()
        _setlogfile()
    except OSError as e:
        logger.warning("OSError: %s" % e)
    # Init database at startup.
    # Database()
    imotionapp = QApplication(sys.argv)
    imotionmain = ImotionMain()
    imotionmain.show()
    sys.exit(imotionapp.exec_())
