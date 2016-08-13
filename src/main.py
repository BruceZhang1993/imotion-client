#!/usr/bin/env python3
#-- coding: utf-8 --

import sys
import json

from PyQt5.QtWidgets import QInputDialog, QCheckBox, QDialog, QListView, QWidget, QLineEdit, QPushButton, QMessageBox, QListWidgetItem, QLabel, QMainWindow, QDesktopWidget, QApplication, QGridLayout, QScrollArea, QListWidget
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal, QModelIndex
from PyQt5.QtGui import QFont, QColor, QStandardItemModel, QStandardItem, QIcon
from connection import IRCConnection, ServerConnectionError, IRCThread

class ImotionMain(QMainWindow):

    currentChannel = None
    channelList = list()
    connection = None

    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):

        # Set window layout
        grid = QGridLayout()
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        centralWidget.setLayout(grid)
        self.setStyleSheet("ImotionMain {background: #ddd;}")

        # Server list and scroll area
        self.serverlist = ServerList()
        self.serverlist.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.serverlist.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        smodel = self.serverlist.selectionModel()
        # smodel.currentChanged.connect(self.selectChannel)

        # self.serverlist.addItems(self.serverlist.items)
        self.nickbtn = ControlButton("")
        self.nickbtn.setToolTip("- 设置昵称 -")
        self.nickbtn.setEnabled(False)
        addserverbtn = ControlButton("")
        addserverbtn.setToolTip("- 连接服务器 -")
        addserverbtn.clicked.connect(self.showserverdialog)
        self.nickbtn.clicked.connect(self.changeNick)
        grid.addWidget(self.serverlist, 0, 0, 2, 4)
        grid.addWidget(self.nickbtn, 1, 0)
        grid.addWidget(addserverbtn, 1, 1)

        # Set main chat panel
        chatgrid = QGridLayout()
        topic = TopicLabel("Example Topic.")
        chatgrid.addWidget(topic, 0, 0, 1, 2)
        grid.addLayout(chatgrid, 0, 6, 0, 35)

        # Chat window
        self.chats = ChatList()
        chatgrid.addWidget(self.chats, 1, 0, 1, 2)
        # chat = [ ChatListOtherMessage("Other's Message."), ChatListMyMessage("My Message."), ChatListInfo("bruceutut joins.") ]
        # self.chats.addItems(chat)

        self.chatinput = ChatInput()
        chatgrid.addWidget(self.chatinput, 2, 0)
        self.chatinput.textChanged.connect(self.setSendState)
        self.chatinput.returnPressed.connect(self.sendMessage)

        self.send = SendButton("")
        chatgrid.addWidget(self.send, 2, 1)
        self.send.clicked.connect(self.sendMessage)

        # Window default position and size
        self.setWindowIcon(QIcon("../icon/imotion.ico"))
        self.resize(800, 500)
        self.center()

        # self.communicator = ImotionCommunicator(self.serverInfo)
        # self.communicator.timeout.connect(self.updateInfo)

        # Set window title
        self.setWindowTitle("I-Motion IM Client")
        # self.communicator.start()
    #
    # def selectChannel(self, curr, last):
    #     ch = curr.text().strip()

    def setSendState(self):
        if self.chatinput.text() == "":
            self.send.disable()
        else:
            self.send.enable()

    def showserverdialog(self):
        sd = ServerDialog(self)
        sd.exec_()
        self.cinfo = sd.cinfo
        # print(self.cinfo)
        if self.cinfo:
            self.connectServer(*self.cinfo)

    def changeNick(self):
        if self.connection:
            text, ok = QInputDialog.getText(self, "NICK", "设置新的NICK:")
            if ok:
                self.connection.connection.nick(text)
                self.nickname = self.connection.connection.get_nickname()
                self.chats.addItems([ChatListInfo("更改 NICK -> %s" % self.nickname)])

    def connectServer(self, *args):
        try:
            self.connection = IRCConnection(*args)
            self.connection.communicator.signalOut.connect(self.proceedMsg)
            # self.connection.communicator.updateInfo.connect(self.proceedInfo)
            self.irc = IRCThread(self.connection)
            self.irc.start()
            self.nickname = self.connection.connection.get_nickname()
            self.servername = self.connection.server
            self.serverlist.addItems([self.servername])
            self.serverlist.addItems(self.connection.channels, True)
            self.channelList = self.connection.channels
            if self.channelList:
                self.currentChannel = self.channelList[0]
            self.nickbtn.setEnabled(True)
        except ServerConnectionError:
            pass

    def proceedMsg(self, jmsg):
        msg = json.loads(jmsg)
        text = msg["nick"] + "| " + msg["msg"]
        self.chats.addItems([ChatListOtherMessage(text)])

    def updateTopic(self, jmsg):
        msg = json.loads(jmsg)
        self.serverInfo[msg["channel"]] = msg["topic"]

    def sendMessage(self):
        message = self.chatinput.text()
        self.chatinput.setText("")
        if message.startswith("//"):
            message = message.replace("//", "/", 1)
            if self.connection:
                self.connection.connection.privmsg(self.currentChannel, message)
                self.chats.addItems(ChatListMyMessage(message))
        elif message.startswith("/"):
            self.proceedCommand(message)
        else:
            if self.connection:
                self.connection.connection.privmsg(self.currentChannel, message)
                self.chats.addItems([ChatListMyMessage(message)])

    def proceedCommand(self, cmds):
        cmdlist = cmds.split()
        if cmdlist[0].strip("/").lower() == "join":
            try:
                self.connection.connection.join(cmdlist[1])
                self.channelList.append(cmdlist[1])
                self.updateServerChannels()
                self.chats.addItems([ChatListInfo("加入 -> %s" % cmdlist[1])])
            except:
                pass

    def updateServerChannels(self):
        self.serverlist.model.clear()
        self.serverlist.addItems([self.servername])
        self.serverlist.addItems(self.channelList, True)

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def closeEvent(self, event):
        confirm = QMessageBox.question(self, "退出...", "确认退出 I-Motion IM 客户端？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                self.connection.connection.quit()
            except:
                pass
            event.accept()
        else:
            event.ignore()

class ServerList(QListView):

    def __init__(self):
        super().__init__()
        self.model = QStandardItemModel(self)
        self.setModel(self.model)

    def addItems(self, items, is_channel=False):
        for item in items:
            self.model.appendRow(ServerListItem(item, is_channel))

class ServerListItem(QStandardItem):

    def __init__(self, text, is_channel=False):
        if is_channel:
            text = " " + text
        super().__init__(text)
        self.is_channel = is_channel
        self.setupUi()

    def setupUi(self):
        self.setBackground(Qt.lightGray)
        font = QFont()
        size = QSize()

        if not self.is_channel:
            font.setPixelSize(16)
            font.setBold(True)
            size.setHeight(25)
        else:
            font.setPixelSize(12)
            size.setHeight(20)
        self.setSizeHint(size)
        self.setFont(font)

class ChatList(QListView):

    def __init__(self):
        super().__init__()
        self.model = QStandardItemModel(self)
        self.setModel(self.model)
        self.setupUi()

    def setupUi(self):
        font = self.font()
        font.setPixelSize(15)
        self.setFont(font)
        self.setVerticalScrollMode(QListView.ScrollPerPixel)
        self.setWordWrap(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("ChatList::item {border: 0px; border-radius: 8px; padding: 10px; color: #000;}")

    def addItems(self, items, p_str=None):
        for item in items:
            self.model.appendRow(item)
        self.scrollToBottom()

class ChatListMyMessage(QStandardItem):

    def __init__(self, text):
        super().__init__(text)
        self.setupUi()

    def setupUi(self):
        self.setTextAlignment(Qt.AlignRight)
        self.setFlags(Qt.NoItemFlags)

class ChatListInfo(QStandardItem):

    def __init__(self, text):
        super().__init__(text)
        self.setupUi()

    def setupUi(self):
        # self.setForeground(QColor(125, 125, 125))
        # self.setBackground(QColor(202, 238, 250))
        self.setTextAlignment(Qt.AlignCenter)
        self.setFlags(Qt.NoItemFlags)

class ChatListOtherMessage(QStandardItem):

    def __init__(self, text):
        super().__init__(text)
        self.setupUi()

    def setupUi(self):
        self.setTextAlignment(Qt.AlignLeft)
        self.setFlags(Qt.NoItemFlags)

class ControlButton(QPushButton):

    def __init__(self, text):
        super().__init__(text)
        self.setupUi()

    def setupUi(self):
        self.setMaximumWidth(30)
        self.setStyleSheet("ControlButton {background: #B8FCD0; padding: 2px;}")

class SendButton(QPushButton):

    def __init__(self, text):
        super().__init__(text)
        self.setupUi()

    def setupUi(self):
        self.setToolTip("-- 请先输入内容 --")
        self.setMaximumWidth(30)
        self.setStyleSheet(
            "SendButton {padding: 4px; background: #aaa; color: #fff; border: 0px transparent; border-radius: 12px;}")

    def disable(self):
        self.setToolTip("-- 请先输入内容 --")
        self.setStyleSheet(
            "SendButton {padding: 4px; background: #aaa; color: #fff; border: 0px transparent; border-radius: 12px;}")
        self.setDisabled(True)

    def enable(self):
        self.setToolTip("-- 发送 --")
        self.setStyleSheet(
            "SendButton {padding: 4px; background: #20C2F7; color: #fff; border: 0px transparent; border-radius: 12px;}")
        self.setEnabled(True)

class ChatInput(QLineEdit):

    def __init__(self):
        super().__init__()
        # self.setupUi()

class ServerDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.cinfo = None
        self.setupUi()

    def setupUi(self):
        layout = QGridLayout()
        self.setLayout(layout)
        self.setStyleSheet("ServerDialog {color: #999}")
        self.setWindowTitle("连接服务器...")
        self.setFixedSize(250, 350)

        # widgets
        slb = QLabel("服务器")
        plb = QLabel("端口")
        splb = QLabel("密码")
        nlb = QLabel("NICK")
        ulb = QLabel("USERNAME")
        rlb = QLabel("REALNAME")
        aulb = QLabel("认证")
        ipv6lb = QLabel("IPv6")
        ssllb = QLabel("SSL")
        chlb = QLabel("自动加入")

        self.sl = PlaceHoldEdit("irc.freenode.net")
        self.pl = PlaceHoldEdit("6667")
        self.spl = PlaceHoldEdit("可选", True)
        self.nl = PlaceHoldEdit()
        self.ul = PlaceHoldEdit("可选")
        self.rl = PlaceHoldEdit("可选")
        self.aul = PlaceHoldEdit("可选", True)
        self.ipv6l = QCheckBox()
        self.ssll = QCheckBox()
        self.chl = PlaceHoldEdit("可选，以空格划分")

        self.nl.textChanged.connect(self.textSync)

        layout.addWidget(slb, 0, 0)
        layout.addWidget(plb, 1, 0)
        layout.addWidget(splb, 2, 0)
        layout.addWidget(nlb, 3, 0)
        layout.addWidget(ulb, 4, 0)
        layout.addWidget(rlb, 5, 0)
        layout.addWidget(aulb, 6, 0)
        layout.addWidget(ssllb, 7, 0)
        layout.addWidget(ipv6lb, 7, 2)
        layout.addWidget(chlb, 8, 0)

        layout.addWidget(self.sl, 0, 1, 1, 3)
        layout.addWidget(self.pl, 1, 1, 1, 3)
        layout.addWidget(self.spl, 2, 1, 1, 3)
        layout.addWidget(self.nl, 3, 1, 1, 3)
        layout.addWidget(self.ul, 4, 1, 1, 3)
        layout.addWidget(self.rl, 5, 1, 1, 3)
        layout.addWidget(self.aul, 6, 1, 1, 3)
        layout.addWidget(self.ssll, 7, 1)
        layout.addWidget(self.ipv6l, 7, 3)
        layout.addWidget(self.chl, 8, 1, 1, 3)

        self.ok = QPushButton("连接")
        self.cancel = QPushButton("取消")
        layout.addWidget(self.cancel, 9, 0, 1, 2)
        layout.addWidget(self.ok, 9, 2, 1, 2)

        self.ok.clicked.connect(self.doOk)
        self.cancel.clicked.connect(self.doCancel)

    def doOk(self):
        if not self.pl.text():
            port = 6667
        else:
            port = int(self.pl.text())
        chs = self.chl.text().split()
        self.cinfo = [self.sl.text() or 'irc.freenode.net', port, self.nl.text(), chs, self.aul.text(), self.spl.text(), self.ul.text(),
                      self.rl.text(),  self.ssll.isChecked(), self.ipv6l.isChecked()]
        self.done(1)

    def doCancel(self):
        self.done(0)

    def textSync(self):
        self.rl.setText(self.nl.text())
        self.ul.setText(self.nl.text())

class PlaceHoldEdit(QLineEdit):

    def __init__(self, placeholder=None, passwd=False):
        super().__init__()
        if placeholder:
            self.setPlaceholderText(placeholder)
        if passwd:
            self.setEchoMode(QLineEdit.Password)
        # self.setStyleSheet("PlaceHoldEdit {margin: 0px;}")

class TopicLabel(QLabel):

    def __init__(self, text):
        super().__init__(text)
        self.setupUi()

    def setupUi(self):
        self.setStyleSheet("TopicLabel {padding: 5px; border: 0px solid grey; border-radius: 5px; background: #ccc;}")

if __name__ == '__main__':
    imotionapp = QApplication(sys.argv)
    imotionmain = ImotionMain()
    imotionmain.show()
    sys.exit(imotionapp.exec_())