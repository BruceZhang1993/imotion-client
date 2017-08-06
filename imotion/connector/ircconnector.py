#!/usr/bin/env python3
# -- coding: utf-8 --

import pydle
import logging
# import threading
from PyQt5.QtCore import QThread, QObject, pyqtSignal
from imotion.const import *

# from src.database import Database
BaseClient = pydle.featurize(
    pydle.features.RFC1459Support,
    pydle.features.CTCPSupport,
    pydle.features.IRCv3_1Support,
    pydle.features.ircv3.SASLSupport
)

logger = logging.getLogger("imotion")


class IRCCommunicator(QObject):

    recv_msg = pyqtSignal(str, str, str)
    priv_msg = pyqtSignal(str, str)
    chan_notice = pyqtSignal(str, str, str)
    join_chan = pyqtSignal(str)
    server_info = pyqtSignal(str)
    chan_info = pyqtSignal(str, str)
    connected = pyqtSignal()

    def __init__(self):
        super().__init__()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(IRCCommunicator, cls).__new__(cls)
        return cls.instance


class IRCClient(BaseClient):

    communicator = IRCCommunicator()

    def __init__(self, nickname, nf, username, realname, autojoin, tls=None,
                 sasl_username=None, sasl_password=None, sasl_identify=None):
        super().__init__(nickname, nf, username, realname)
        self.passwd = sasl_password
        self.chans = autojoin or []

    def on_connect(self):
        self.communicator.connected.emit()
        if self.passwd:
            self.message('NickServ', 'identify %s' % self.passwd)
            logger.info("Sent nickserv identify message.")
        for ch in self.chans:
            self.join(ch)
            self.communicator.join_chan.emit(ch)

    def on_unknown(self, msg):
        # TODO msg
        # self.communicator.server_info('[UNKNOWN] ' + msg)
        pass

    def on_join(self, channel, user):
        logger.debug("[JOIN] %s -> %s" % (user, channel))
        self.communicator.chan_info.emit(
            channel, "[JOIN] %s joined %s" % (user, channel))

    def on_invite(self, channel, by):
        logger.debug("[INVITE] %s from %s" % (channel, by))
        self.communicator.server_info.emit(
            "[INVITE] %s invited you to join channel %s" % (by, channel))

    def on_channel_message(self, target, by, message):
        logger.debug("[CHAN_MSG] from %s to %s: %s" % (by, target, message))
        self.communicator.recv_msg.emit(target, by, message)

    def on_private_message(self, by, message):
        logger.debug("[PRIV_MSG] from %s: %s" % (by, message))
        self.communicator.priv_msg.emit(by, message)

    def on_channel_notice(self, target, by, message):
        logger.debug("[CHAN_NOTICE] from %s to %s: %s" % (by, target, message))
        self.communicator.chan_notice.emit(target, by, message)

    def on_private_notice(self, by, message):
        logger.debug("[PRIV_NOTICE] %s from %s" % (message, by))
        self.communicator.server_info.emit(
            "[NOTICE] %s from %s" % (message, by))

    def on_kick(self, channel, target, by, reason=None):
        logger.debug("[KICK] %s kicked %s from %s for %s" %
                     (by, target, channel, reason or "no reason"))
        self.communicator.chan_info.emit(
            channel, "[KICK] %s kicked by %s for %s" % (target, by,
                                                        reason or "no reason"))

    def on_kill(self, target, by, reason):
        logger.debug("[KILL] %s killed from server by %s for %s" %
                     (target, by, reason or 'no reason'))
        self.communicator.server_info.emit(
            "[KILL] %s killed from server by %s for %s" % (target,
                                                           by, reason or 'no reason'))

    def on_topic_change(self, channel, message, by):
        logger.debug("[TOPIC] %s changed topic %s by %s" %
                     (channel, message, by))
        self.communicator.chan_info.emit(
            channel, "[TOPIC] topic changed to %s by %s" % (message, by))

    def on_quit(self, user, message):
        logger.debug("[QUIT] %s client quit for %s" %
                     (user, message or 'no reason'))
        self.communicator.server_info.emit("[QUIT] %s client quit for %s" %
                                           (user, message or 'no reason'))

    def on_user_mode_change(self, modes):
        logger.debug("[USER_MODE] changed to %s" % modes)
        self.communicator.server_info.emit("[USER_MODE] changed to %s" % modes)

    def on_mode_change(self, channel, modes, by):
        logger.debug("[MODE] %s mode changed to %s by %s" %
                     (channel, modes, by))
        self.communicator.chan_info.emit(
            channel, "[MODE] mode changed to %s by %s" % (modes, by))

    def on_part(self, channel, user, message=None):
        logger.debug("[PART] %s <- %s for %s" %
                     (user, channel, message or 'no reason'))
        self.communicator.chan_info.emit(channel, "[PART] %s left for %s" %
                                         (user, message or 'no reason'))

    def on_ctcp(self, by, target, what, contents):
        logger.debug("[CTCP] %s %s to %s by %s" % (what, contents, target, by))
        self.communicator.server_info.emit(
            "[CTCP] %s %s to %s by %s" % (what, contents, target, by))
        ctcps = {
            "version": ["VERSION", "%s %s %s" % (APPNAME, VERSION, TRUNK)],
            "ping": ["PONG", None]
        }
        if what.lower() in ctcps.keys():
            self.ctcp_reply(by, *ctcps[what.lower()])

    def on_ctcp_reply(self, by, target, what, response):
        logger.debug("[CTCP_REPLY] %s %s to %s by %s" %
                     (what, response, target, by))
        self.communicator.server_info.emit(
            "[CTCP_REPLY] %s %s to %s by %s" % (what, response, target, by))

    def on_nick_change(self, old, new):
        logger.debug("[NICK_CHANGE] %s -> %s" % (old, new))
        self.communicator.server_info.emit(
            "[NICK_CHANGE] %s changed nickname to %s" % (old, new))


class IRCConnector(QThread):

    communicator = IRCCommunicator()

    def __init__(self):
        super().__init__()
        # self.db = Database().default

    def connect_server(self, server, port, nickname, username=None,
                       realname=None, autojoin=None, tls=False,
                       sasl_username=None, sasl_password=None,
                       sasl_identify=None, ssl_verify=False):
        self.client = IRCClient(nickname, [nickname + '_', nickname + '__'],
                                username or nickname, realname or nickname,
                                autojoin=autojoin, sasl_username=sasl_username,
                                sasl_password=sasl_password,
                                sasl_identify=sasl_identify)
        self.client.connect(server, port, tls=tls, tls_verify=ssl_verify)

    def run(self):
        self.client.handle_forever()
