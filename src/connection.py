#!/usr/bin/env python3
#-- coding: utf-8 --

import logging
import irc.client
import irc.connection
from ssl import SSLContext

logger = logging.getLogger('IRC')

class IRCConnection(irc.client.SimpleIRCClient):

    def __init__(self, server, port, nickname,
                 channels=list(), passwd=None, serverpass=None, username=None, realname=None, ssl=False, ipv6=False):
        super().__init__()
        ssl_factory = irc.connection.Factory()
        if ssl:
            ssl_factory.from_legacy_params(ssl=True)
        if ipv6:
            ssl_factory.from_legacy_params(ipv6=True)
        try:
            self.connect(server, port, nickname, password=serverpass, username=username,
            ircname=realname, connect_factory=ssl_factory)
        except irc.client.ServerConnectionError as e:
            logger.error("Cannot connect to server.")
        self.channels = channels
        self.passwd = passwd

    def on_welcome(self, c, e):
        if self.passwd:
            c.privmsg("NickServ", "identify %s" % self.passwd)
        for channel in self.channels:
            if irc.client.is_channel(channel):
                c.join(channel)

    def on_pubmsg(self, c, e):
        print(e.target + e.arguments[0])

    def on_privmsg(self, c, e):
        print(e.source.nick + e.arguments[0])

if __name__ == '__main__':
    connection = IRCConnection("irc.freenode.net", 7000, "brucetest", channels=["#brucetest"], ssl=True, username="brucetest", realname="Bruce Test")
    connection.start()