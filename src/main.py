#!/usr/bin/env python3
#-- coding: utf-8 --

import sys

from PyQt5.QtWidgets import QButtonGroup, QWidget, QPushButton, QMessageBox, QListWidgetItem, QLabel, QMainWindow, QDesktopWidget, QApplication, QGridLayout, QScrollArea, QListWidget
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor


class ImotionMain(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):

        # Set window layout
        grid = QGridLayout()
        self.setLayout(grid)
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        centralWidget.setLayout(grid)
        self.setStyleSheet("ImotionMain {background: #ddd;}")

        # Server list and scroll area
        serverlist = ServerList()
        serverlist.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        serverlist.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        items = [ ServerListItem("Test Server", False), ServerListItem("#Test Channel", True) ]
        serverlist.addItems(items)
        nickbtn = ControlButton("N")
        addserverbtn = ControlButton("S")
        grid.addWidget(serverlist, 0, 0, 2, 4)
        grid.addWidget(nickbtn, 1, 0)
        grid.addWidget(addserverbtn, 1, 1)

        # Set main chat panel
        chatgrid = QGridLayout()
        topic = TopicLabel("Example Topic.")
        chatgrid.addWidget(topic, 0, 0)
        grid.addLayout(chatgrid, 0, 6, 0, 35)

        # Chat window
        chats = ChatList()
        chatgrid.addWidget(chats, 1, 0)
        chat = [ ChatListOtherMessage("Other's Message."), ChatListMyMessage("My Message.") ]
        chats.addItems(chat)

        # Window default position and size
        self.resize(800, 500)
        self.center()

        # Set window title
        self.setWindowTitle("I-Motion IM Client")

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def closeEvent(self, event):
        confirm = QMessageBox.question(self, "退出...", "确认退出 I-Motion IM 客户端？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

class ServerList(QListWidget):

    def __init__(self):
        super().__init__()

    def addItems(self, items, p_str=None):
        for item in items:
            self.addItem(item)

class ServerListItem(QListWidgetItem):

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

class ChatList(QListWidget):

    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        self.setStyleSheet("ChatList::item {border: 0px; border-radius: 8px; padding: 10px; color: #000;}")

    def addItems(self, items, p_str=None):
        for item in items:
            self.addItem(item)

class ChatListMyMessage(QListWidgetItem):

    def __init__(self, text):
        super().__init__(text)
        self.setupUi()

    def setupUi(self):
        self.setTextAlignment(Qt.AlignRight)
        self.setFlags(Qt.NoItemFlags)

class ChatListOtherMessage(QListWidgetItem):

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

class TopicLabel(QLabel):

    def __init__(self, text):
        super().__init__(text)
        self.setupUi()

    def setupUi(self):
        self.setStyleSheet("TopicLabel {border: 1px solid; border-radius: 4px; background: #ccc;}")

if __name__ == '__main__':
    imotionapp = QApplication(sys.argv)
    imotionmain = ImotionMain()
    imotionmain.show()
    sys.exit(imotionapp.exec_())