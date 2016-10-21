#!/usr/bin/env python3
# -- coding: utf-8 --

import pydle
import logging
from PyQt5.QtCore import QThread, QObject, pyqtSignal

# from src.database import Database
# BaseClient = pydle.featurize(
#     pydle.features.RFC1459Support,
#     pydle.features.CTCPSupport,
#     pydle.features.AccountSupport,
#     pydle.features.IRCv3Support
# )

logger = logging.getLogger("imotion")


class IRCCommunicator(QObject):

    recv_msg = pyqtSignal(str, str, str)

    def __init__(self):
        super().__init__()


class IRCClient(pydle.Client):

    communicator = IRCCommunicator()

    def __init__(self, nickname, nf, username, realname, autojoin, tls=None,
                 sasl_username=None, sasl_password=None, sasl_identify=None):
        super().__init__(nickname, nf, username, realname)
        self.passwd = sasl_password
        self.chans = autojoin or []

    def on_connect(self):
        self.message('NickServ', 'identify %s' % self.passwd)
        for ch in self.chans:
            self.join(ch)

    def on_message(self, target, by, message):
        logger.debug("[MSG]from %s to %s: %s" % (by, target, message))
        self.communicator.recv_msg.emit(target, by, message)


class IRCConnector(QThread):

    def __init__(self):
        super().__init__()
        # self.db = Database().default

    def connect_server(self, server, port, nickname, username=None,
                       realname=None, autojoin=None, tls=False,
                       sasl_username=None, sasl_password=None,
                       sasl_identify=None):
        self.client = IRCClient(nickname, [nickname + '_', nickname + '__'],
                                username or nickname, realname or nickname,
                                autojoin=autojoin, sasl_username=sasl_username,
                                sasl_password=sasl_password,
                                sasl_identify=sasl_identify)
        self.client.connect(server, port, tls=tls)

    def run(self):
        self.client.handle_forever()
