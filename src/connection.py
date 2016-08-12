#!/usr/bin/env python3
#-- coding: utf-8 --

import logging
import irc.client
import irc.connection
from PyQt5.QtCore import pyqtSignal, QObject, QThread
import json

logger = logging.getLogger('IRC')

class Communicator(QObject):

    signalOut = pyqtSignal(str)
    updateInfo = pyqtSignal(dict)

class IRCThread(QThread):

    def __init__(self, connection):
        self.connection = connection
        super().__init__()

    def run(self):
        self.connection.start()

class IRCConnection(irc.client.SimpleIRCClient):

    def __init__(self, server, port, nickname,
                 channels=list(), passwd=None, serverpass=None, username=None, realname=None, ssl=False, ipv6=False):
        irc.client.SimpleIRCClient.__init__(self)
        self.communicator = Communicator()
        self.server = server
        self.nickname = nickname
        self.port = port
        self.channels = channels
        self.passwd = passwd
        self.serverpass = serverpass
        self.username = username
        self.realname = realname
        self.ssl_factory = irc.connection.Factory()
        if ssl:
            self.ssl_factory.from_legacy_params(ssl=True)
        if ipv6:
            self.ssl_factory.from_legacy_params(ipv6=True)
        self.channels = channels
        self.passwd = passwd
        # self.reactor.execute_every(5, self.updateInfos)
        self._connect()

    def on_welcome(self, c, e):
        if self.passwd:
            c.privmsg("NickServ", "identify %s" % self.passwd)
        for channel in self.channels:
            if irc.client.is_channel(channel):
                c.join(channel)

    def on_pubmsg(self, c, e):
        obj = {"type": "pubmsg", "nick": e.source.nick, "channel": e.target, "msg": e.arguments[0]}
        jmsg = json.dumps(obj)
        self.communicator.signalOut.emit(jmsg)

    def on_privmsg(self, c, e):
        obj = {"type": "privmsg", "nick": e.source.nick, "msg": e.arguments[0]}
        jmsg = json.dumps(obj)
        self.communicator.signalOut.emit(jmsg)

    def _connect(self):
        try:
            self.connect(self.server, self.port, self.nickname, password=self.serverpass, username=self.username,
            ircname=self.realname, connect_factory=self.ssl_factory)
        except irc.client.ServerConnectionError as e:
            logger.error("%s: Cannot connect to server." % e)
            raise ServerConnectionError(e)

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")
        info = {"nick": c.get_nickname()}
        self.communicator.updateInfo.emit(json.dumps(info))

class ServerConnectionError(Exception):

    def __init__(self, err):
        self.err = err

    def __str__(self):
        return "%s: Cannot connect to server." % self.err

if __name__ == '__main__':
    connection = IRCConnection("irc.freenode.net", 6667, "brucetest", channels=["brucetest"], ssl=False, username="brucetest", realname="Bruce Test")
    connection.start()