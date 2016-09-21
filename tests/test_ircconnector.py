#!/usr/bin/env python3
#-- coding: utf-8 --

import unittest

from src.connector.ircconnector import IRCClient, IRCConnector


class IRCConnectorTestCase(unittest.TestCase):

    def setUp(self):
        self.pool = IRCConnector()
        self.pool.connect_server('irc.freenode.net', 6667, "test_bruce", autojoin=["#testbruce"])
        self.pool.connect_server('irc.freenode.net', 7000, "test_bruce2", autojoin=["#testbruce"], tls=True)

    def test_ircclient_connect(self):
        self.pool.start()
        # for client in self.pool.children():
        #     client.message("#testbruce", "Hello, just testing.")

    def tearDown(self):
        for client in self.pool.children():
            self.pool.disconnect(client)
        self.pool.quit()

if __name__ == '__main__':
    unittest.main()