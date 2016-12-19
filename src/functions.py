#!/usr/bin/env python3
# -- coding: utf-8 --

import os
import logging
import errno
import re

from const import COLORS


def create_dir(dir):
    logger = logging.getLogger('imotion')
    try:
        os.mkdir(dir)
        if os.sys.platform == 'win32':
            import ctypes
            FILE_ATTRIBUTE_HIDDEN = 0x02
            ret = ctypes.windll.kernel32.SetFileAttributesW(dir,
                                                            FILE_ATTRIBUTE_HIDDEN)
            logger.info("Trying to hide app dir.")
        logger.info("FirstRun: DIR %s has been created successfully." % dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e
        else:
            logger.debug("DIR %s exists. Ignoring..." % dir)


def parse_color(message):
    msg_list = message.split("\x02")
    message = "".join(map(lambda x: append_tag(x[1], bold=True)
                          if x[0] % 2 == 1 else x[1], enumerate(msg_list)))
    msg_list = message.split("\x1F")
    message = "".join(map(lambda x: append_tag(x[1], underline=True)
                          if x[0] % 2 == 1 else x[1], enumerate(msg_list)))
    msg_list = message.split("\x1D")
    message = "".join(map(lambda x: append_tag(x[1], itatic=True)
                          if x[0] % 2 == 1 else x[1], enumerate(msg_list)))
    msg_list = message.split("\x03")
    message = "".join(map(lambda x: proceed_colorstr(x[1])
                          if x[0] % 2 == 1 else x[1], enumerate(msg_list)))
    return message


def proceed_colorstr(str):
    reg = re.compile(r'(\d{1,2}),?(\d{1,2})?')
    result, n = reg.subn('', str)
    clrs = reg.match(str)
    fore = clrs.group(1)
    back = False
    try:
        back = clrs.group(2)
    except IndexError as e:
        return append_tag(result, forecolor=COLORS[int(fore) if int(fore) < len(COLORS) else 1],
                          backcolor=False)
    if back:
        return append_tag(result, forecolor=COLORS[int(fore) if int(fore) < len(COLORS) else 1],
                          backcolor=COLORS[int(back) if int(back) < len(COLORS) else 0])
    else:
        return append_tag(result, forecolor=COLORS[int(fore) if int(fore) < len(COLORS) else 1],
                          backcolor=False)


def append_tag(message, forecolor=False, backcolor=False, bold=False, itatic=False, underline=False):
    styleStr = ""
    styleStr += "color:%s;" % forecolor if forecolor else ""
    styleStr += "background:%s;" % backcolor if backcolor else ""
    styleStr += "font-weight:bold;" if bold else ""
    styleStr += "font-style:oblique;" if itatic else ""
    styleStr += "text-decoration:underline;" if underline else ""
    return "<span style='%s'>%s</span>" % (styleStr, message)
