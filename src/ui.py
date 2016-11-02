#!/usr/bin/env python3
# -- coding: utf-8 --

from connector.ircconnector import IRCConnector
from const import *
from PyQt5.QtWidgets import QGridLayout, QApplication, QTabWidget, QWidget, \
    QLineEdit, QPushButton, QDialog, QLabel, QCheckBox, QTextEdit
from PyQt5.QtGui import QTextOption
# from PyQt5.QtCore import QThread
from time import strftime


class Ui_main(object):

    def setup_Ui(self, win):
        win.setWindowTitle("%s - %s" % (APPNAME, TRUNK))
        win.resize(700, 480)
        desktop = QApplication.desktop()
        win.move((desktop.width() - win.width()) / 2,
                 (desktop.height() - win.height()) / 2)
        win.layout = QGridLayout()
        win.setLayout(win.layout)
        win.tabwidget = QTabWidget()
        win.page1 = QTextEdit()
        win.page1.setReadOnly(True)
        win.page1.setWordWrapMode(QTextOption.NoWrap)
        win.tabwidget.addTab(win.page1, "Server")
        win.layout.addWidget(win.tabwidget, 0, 0, 1, 3)
        win.chat = ChatInput("Text Here...", parent=win)
        win.layout.addWidget(win.chat, 1, 1, 1, 2)
        # win.chatsend = ChatSend()
        # win.layout.addWidget(win.chatsend, 1, 2)
        win.loginbtn = QPushButton("Login")
        win.loginbtn.setMaximumWidth(50)
        win.layout.addWidget(win.loginbtn, 1, 0)


class Ui_login(object):

    def setup_Ui(self, win):
        win.resize(300, 400)
        win.setWindowTitle("Login")
        win.layout = QGridLayout()
        win.setLayout(win.layout)

        win.serverlb = QLabel("服务器")
        win.portlb = QLabel("端口")
        win.serverpasslb = QLabel("密码")
        win.nicklb = QLabel("昵称")
        win.userlb = QLabel("用户名")
        win.reallb = QLabel("真实姓名")
        win.authlb = QLabel("验证")

        win.server = DialogInput(None)
        win.port = DialogInput("6667")
        win.serverpass = DialogInput("Optional", passwd=True)
        win.nick = DialogInput(None)
        win.user = DialogInput(None)
        win.real = DialogInput(None)
        win.auth = DialogInput("Optional", passwd=True)
        win.showauth = QPushButton("Show")
        win.ssl = IMCheckBox("SSL", True)
        win.ipv6 = QCheckBox("IPv6")
        win.chanlb = QLabel("自动加入")
        win.chan = DialogInput("以空格分隔")
        win.confirm = QPushButton("连接")
        win.cancel = QPushButton("取消")

        # Use for debugging
        win.server.setText("irc.freenode.net")
        win.chan.setText("#linuxba #archlinux-cn")
        win.ssl.setChecked(False)

        win.layout.addWidget(win.serverlb, 0, 0)
        win.layout.addWidget(win.server, 0, 1, 1, 3)
        win.layout.addWidget(win.portlb, 1, 0)
        win.layout.addWidget(win.port, 1, 1, 1, 3)
        win.layout.addWidget(win.serverpasslb, 2, 0)
        win.layout.addWidget(win.serverpass, 2, 1, 1, 3)
        win.layout.addWidget(win.nicklb, 3, 0)
        win.layout.addWidget(win.nick, 3, 1, 1, 3)
        win.layout.addWidget(win.userlb, 4, 0)
        win.layout.addWidget(win.user, 4, 1, 1, 3)
        win.layout.addWidget(win.reallb, 5, 0)
        win.layout.addWidget(win.real, 5, 1, 1, 3)
        win.layout.addWidget(win.authlb, 6, 0)
        win.layout.addWidget(win.auth, 6, 1, 1, 2)
        win.layout.addWidget(win.showauth, 6, 3)
        win.layout.addWidget(win.ssl, 7, 0, 1, 2)
        win.layout.addWidget(win.ipv6, 7, 2, 1, 2)
        win.layout.addWidget(win.chanlb, 8, 0)
        win.layout.addWidget(win.chan, 8, 1, 1, 3)
        win.layout.addWidget(win.cancel, 9, 2)
        win.layout.addWidget(win.confirm, 9, 3)


class IMCheckBox(QCheckBox):
    def __init__(self, text, checked=False):
        super().__init__(text, None)
        self.setChecked(checked)


class DialogInput(QLineEdit):

    def __init__(self, text, passwd=False):
        super().__init__()
        self.setPlaceholderText(text)
        if passwd:
            self.setEchoMode(QLineEdit.Password)


class ImotionMain(QWidget):

    channels = []
    curr_chan = None
    pages = {}
    irc = None

    def __init__(self):
        super().__init__()
        self.setupUi()
        self.loginbtn.clicked.connect(self.showlogin)
        self.tabwidget.currentChanged.connect(self.set_currchan)

    def set_currchan(self, index):
        self.curr_chan = self.channels[index - 1]

    def setupUi(self):
        self.ui = Ui_main()
        self.ui.setup_Ui(self)

    def change_nick(self):
        pass

    def _append_chan(self, channel):
        self.channels.append(channel.strip())
        self.pages[channel.strip()] = QTextEdit()
        self.pages[channel.strip()].setReadOnly(True)
        self.tabwidget.addTab(self.pages[channel.strip()], channel.strip())

    def chan_notice(self, target, by, message):
        if target.strip() not in self.channels:
            self._append_chan(target)
        self.pages[target.strip()].append("(%s) %s NOTICE: | %s" %
                                          (strftime("%H:%M"), by, message))

    def joined_chan(self, channel):
        self._append_chan(channel)

    def priv_msg(self, by, message):
        if by.strip() not in self.channels:
            self._append_chan(by)
        self.pages[by.strip()].append("(%s) %s" %
                                      (strftime("%H:%M"), message))

    def server_info(self, message):
        self.page1.append(message)

    def chan_info(self, channel, message):
        if channel.strip() not in self.channels:
            self._append_chan(channel)
        self.pages[channel.strip()].append("* %s" % message)

    def recv_msg(self, target, by, message):
        if target.strip() not in self.channels:
            self._append_chan(target)
        self.pages[target.strip()].append("(%s) %s | %s" %
                                          (strftime("%H:%M"), by, message))

    def excute_cmd(line):
        logger.debug("[COMMAND] Received command `%s` try excuting..." % line)
        command = line.split()[0]
        args = line.split()[1:]
        _do_command(command, args)

    def _do_command(self, cmd, args):
        if cmd.lower() == 'ctcp':
            

    def send_msg(self, msg):
        if not msg.startswith('/'):
            self.irc.client.message(self.curr_chan, msg)
            self.pages[self.curr_chan].append(
                "(%s) ME | %s" % (strftime("%H:%M"), msg))
        elif msg.startswith('//'):
            self.irc.client.message(self.curr_chan, msg[1:])
            self.pages[self.curr_chan].append(
                "(%s) ME | %s" % (strftime("%H:%M"), msg[1:]))
        else:
            self.excute_cmd(msg.strip('/'))

    def showlogin(self):
        self.loginwin = LoginWindow(self)
        self.loginwin.show()

    def closeEvent(self, event):
        try:
            if self.irc:
                self.irc.client.disconnect()
        finally:
            event.accept()

    def start_connect(self, child):
        self.irc = IRCConnector()
        use_ssl = False
        use_sasl = False
        if child.ssl.checkState == Qt.Checked:
            use_ssl = True
        if child.auth.text():
            use_sasl = True
        self.irc.communicator.join_chan.connect(self.joined_chan)
        self.irc.connect_server(child.server.text(),
                                int(child.port.text())
                                if child.port.text() else 6667,
                                child.nick.text(), username=child.user.text(),
                                realname=child.real.text(),
                                autojoin=child.chan.text().split(),
                                tls=use_ssl,
                                sasl_username=child.user.text()
                                if use_sasl else None,
                                sasl_password=child.auth.text()
                                if use_sasl else None,
                                sasl_identify='' if use_sasl else None)
        self.irc.start()
        self.irc.client.communicator.recv_msg.connect(self.recv_msg)
        self.irc.client.communicator.priv_msg.connect(self.priv_msg)
        self.irc.client.communicator.chan_notice.connect(self.chan_notice)
        self.irc.client.communicator.server_info.connect(self.server_info)
        self.irc.client.communicator.chan_info.connect(self.chan_info)
        self.loginbtn.clicked.disconnect(self.showlogin)
        self.loginbtn.clicked.connect(self.change_nick)


class LoginWindow(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setupUi()
        self.cancel.clicked.connect(self.close)
        self.nick.textEdited.connect(self.sync_text)
        self.showauth.clicked.connect(self.toggle_pass)
        self.confirm.clicked.connect(self.do_connect)

    def do_connect(self):
        if self.nick and self.server:
            self.parent.start_connect(self)
            self.close()

    def toggle_pass(self):
        if self.auth.echoMode() == QLineEdit.Password:
            self.auth.setEchoMode(QLineEdit.Normal)
            self.showauth.setText("Hide")
        else:
            self.auth.setEchoMode(QLineEdit.Password)
            self.showauth.setText("Show")

    def sync_text(self):
        self.user.setText(self.nick.text())
        self.real.setText(self.nick.text())

    def setupUi(self):
        self.ui = Ui_login()
        self.ui.setup_Ui(self)


class ChatInput(QLineEdit):

    def __init__(self, text, parent=None):
        super().__init__()
        self.parent = parent
        self.setupUi()
        self.setPlaceholderText(text)

    def setupUi(self):
        pass

    def keyReleaseEvent(self, event):
        if event.key() in KEYENTER:
            message = self.text()
            self.setText("")
            self.parent.send_msg(message)
        event.accept()


class ChatSend(QPushButton):

    def __init__(self):
        super().__init__(None)
        self.setupUi()

    def setupUi(self):
        self.setText("Send")
