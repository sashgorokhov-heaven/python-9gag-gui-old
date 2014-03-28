__author__ = 'Alexander'
from PyQt4 import QtCore, QtGui
from os import sep

from libs import vkpost, constants
from libs.gorokhovlibs.vk.api import VKApi
from libs.gorokhovlibs.qt.qtwindow import BaseQtWindow
from libs.gorokhovlibs.threading import threaded
from libs.util import GagLabel, CountLabel, GagFeed, showmessage
from resourses.editListItem import editListItem


class MainForm(BaseQtWindow):
    def __init__(self, access_token):
        super().__init__(self, 'resourses' + sep + 'MainForm.ui')
        self.exiting = False
        self.mode = "feed" # feed -> editing -> back
        self.setupGUI()
        self.api = VKApi(access_token)
        self.feed = GagFeed(self)
        self.connect(self, QtCore.SIGNAL("addItem(QString)"), self.feed.addItem)
        self.feed.getFeed()

    def setupGUI(self):
        self.elements.gagLabel = GagLabel(self)
        self.elements.gagLabel.adjust()
        self.elements.countLabel = CountLabel(self, self.elements.countLabel)

        #self.elements.feedList.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        #self.setLayout(self.elements.verticalLayout)
        style = """\
            QScrollBar:vertical  {
                background: none;
                background-color: rgb(81, 81, 81);
                width: 15px;
            }
            QScrollBar::handle:vertical  {
                background: rgb(66, 66, 66);
                border-radius: 10px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical  {
                background: none;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical  {
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical  {
                background: none;
            }
        """
        self.elements.feedList.verticalScrollBar().setStyleSheet(style)
        self.elements.editList.verticalScrollBar().setStyleSheet(style)
        self.elements.stackedWidget.lower()

    def _set_connections(self):
        self.connect(self, QtCore.SIGNAL("setStyleSheet(QString, int)"), self.setStyleSheetSignal)
        self.elements.feedList.verticalScrollBar().valueChanged.connect(self.handle_scrollBarValue)
        self.elements.nextButton.clicked.connect(self.nextButtonClicked)

    @threaded
    def post(self):
        for n, item in enumerate(self.iterateEditItems()):
            if self.exiting:
                return
            widget = self.elements.editList.itemWidget(item)
            self.emit(QtCore.SIGNAL("setStyleSheet(QString, int)"), "background-color: rgb(148, 205, 255)", n)
            try:
                vkpost.post(self.api, self.feed.news[widget.id])
            except Exception as e:
                showmessage('Error while posting: ' + str(e))
                self.emit(QtCore.SIGNAL("setStyleSheet(QString, int)"), "background-color: rgb(255, 117, 112)", n)
                continue
            self.emit(QtCore.SIGNAL("setStyleSheet(QString, int)"), "background-color: rgb(161, 255, 144)", n)
            self.feed.news[widget.id]['posted'] = True
            self.feed.news[widget.id]['feedwidget'].setPosted()
            self.elements.countLabel.dec()
        self.elements.nextButton.setEnabled(True)

    def handle_scrollBarValue(self, value):
        scrollbar = self.elements.feedList.verticalScrollBar()
        if value != scrollbar.maximum(): return
        if not self.feed.loading:
            self.feed.getFeed()

    def setStyleSheetSignal(self, style, item_n):
        self.elements.editList.itemWidget(self.elements.editList.item(item_n)).setStyleSheet(style)

    def nextButtonClicked(self):
        if self.mode == 'feed':
            self.mode = 'editing'
            self.elements.nextButton.setText("Загрузить!")
            for widget in self.iterateFeedWidgets():
                if widget.checked():
                    item = QtGui.QListWidgetItem()
                    myItem = editListItem(widget.id, item, self)
                    self.elements.editList.addItem(item)
                    self.elements.editList.setItemWidget(item, myItem)
            self.stackedWidget.setCurrentIndex(1)
            self.elements.nextButton.setEnabled(True)
            return
        if self.mode == 'editing':
            self.elements.nextButton.setEnabled(False)
            self.post()
            self.elements.nextButton.setText("<- Назад")
            self.mode = 'back'
            return
        if self.mode == 'back':
            self.elements.nextButton.setEnabled(False)
            self.elements.nextButton.setText("-> Далее")
            self.mode = 'feed'
            self.elements.editList.clear()
            self.elements.stackedWidget.setCurrentIndex(0)

    def iterateFeedWidgets(self):
        for i in range(self.elements.feedList.count()):
            yield self.elements.feedList.itemWidget(self.elements.feedList.item(i))

    def iterateFeedItems(self):
        for i in range(self.elements.feedList.count()):
            yield self.elements.feedList.item(i)

    def iterateEditItems(self):
        for i in range(self.elements.editList.count()):
            yield self.elements.editList.item(i)

    def iterateEditWidget(self):
        for i in range(self.elements.editList.count()):
            yield self.elements.editList.itemWidget(self.elements.editList.item(i))

    def resizeEvent(self, event):
        self.elements.gagLabel.adjust()

    def closeEvent(self, event):
        self.exiting = True
        event.accept()