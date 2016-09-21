#!/usr/bin/env python3
#-- coding: utf-8 --

import pydle
from PyQt5.QtCore import QThread

from src.database import Database

class IRCClient(pydle.Client):

    def __init__(self, nickname, nf, username, realname, autojoin):
        super().__init__(nickname, nf, username, realname)
        self.channels = list(map(lambda s:s.strip('#').lower(), autojoin or []))

    def on_connect(self):
        super().on_connect()
        for ch in self.channels:
            self.join('#'+ch)

class IRCConnector(QThread):

    def __init__(self):
        super().__init__(self)
        self.db = Database().default
        self.pool = pydle.client.ClientPool()

    def connect_server(self, server, port, nickname, username=None, realname=None, autojoin=None, tls=False):
        client = IRCClient(nickname, [nickname+'_', nickname+'__'], username or nickname, realname or nickname, autojoin=autojoin)
        self.pool.connect(client, server, port, tls=tls)

    def run(self):
        self.pool.handle_forever()

