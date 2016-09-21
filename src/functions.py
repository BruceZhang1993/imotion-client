#!/usr/bin/env python3
#-- coding: utf-8 --

import os, logging, errno

def create_dir(dir):
    logger = logging.getLogger('imotion')
    try:
        os.mkdir(dir)
        logger.info('FirstRun: DIR %s has been created successfully.')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e
        else:
            logger.debug('DIR %s exists. Ignoring...')
