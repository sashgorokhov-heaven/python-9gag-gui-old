__author__ = 'Alexander'
from PyQt4 import QtCore
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
        self.mode = "feed"
        self.setupGUI()
        self.api = VKApi(access_token)
        self.feed = GagFeed(self)
        self.connect(self, QtCore.SIGNAL("add_item(QString, QString, int, QString)"), self.feed.add_item)
        self.feed.getFeed()

    def setupGUI(self):
        self.elements.gagLabel = GagLabel(self)
        self.elements.gagLabel.adjust()
        self.elements.countLabel = CountLabel(self, self.elements.countLabel)

        #self.elements.feedList.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        #self.setLayout(self.elements.verticalLayout)
        self.elements.feedList.verticalScrollBar().setStyleSheet("""\
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
        """)
        self.elements.feedList.lower()

    def _set_connections(self):
        self.connect(self, QtCore.SIGNAL("setStyleSheet(QString, int)"), self.setStyleSheetSignal)
        self.elements.feedList.verticalScrollBar().valueChanged.connect(self.handle_scrollBarValue)
        self.elements.nextButton.clicked.connect(self.nextButtonClicked)

    def vk_post(self, label, link, imagePath, item):
        aid = vkpost.get_album(self.api, constants.groups['ru9gag'])
        post_type = self.get_post_type(item)
        if post_type == 'wall delay':
            delay = item.elements.dateTimeEdit.dateTime().toTime_t()
            vkpost.wall_post_later(self.api, constants.groups['ru9gag'], label, link, imagePath, delay)
        elif post_type == 'wall now':
            vkpost.wall_post_now(self.api, constants.groups['ru9gag'], label, link, imagePath)
        else:
            vkpost.album_post(self.api, constants.groups['ru9gag'], aid, label, link, imagePath)

    def get_post_type(self, item):
        if item.elements.directWallRB.isChecked():
            if item.elements.waitUntilCheckBox.isChecked():
                return "wall delay"
            return "wall now"
        return "album"

    @threaded
    def post(self):
        for n, item in enumerate(self.iterateFeedWidgets()):
            if self.exiting:
                return
            self.emit(QtCore.SIGNAL("setStyleSheet(QString, int)"), "background-color: rgb(148, 205, 255)", n)
            try:
                self.vk_post(item.caption, item.link, item.imagePath, item)
            except Exception as e:
                showmessage('Error while posting: ' + str(e))
                self.emit(QtCore.SIGNAL("setStyleSheet(QString, int)"), "background-color: rgb(255, 117, 112)", n)
                continue
            self.emit(QtCore.SIGNAL("setStyleSheet(QString, int)"), "background-color: rgb(161, 255, 144)", n)
            self.elements.countLabel.dec()

    def handle_scrollBarValue(self, value):
        if self.mode == 'editing': return
        scrollbar = self.elements.feedList.verticalScrollBar()
        if value != scrollbar.maximum(): return
        if not self.feed.loading:
            self.feed.getFeed()

    def setStyleSheetSignal(self, style, item_n):
        self.elements.feedList.itemWidget(self.elements.feedList.item(item_n)).setStyleSheet(style)

    def nextButtonClicked(self):
        if self.mode == 'editing':
            self.elements.nextButton.setEnabled(False)
            self.post()
            return
        self.mode = 'editing'
        self.elements.nextButton.setText("Загрузить!")
        i = 0
        while i < self.elements.feedList.count():
            item = self.elements.feedList.item(i)
            itemWidget = self.elements.feedList.itemWidget(item)
            if not itemWidget.checked():
                self.elements.feedList.takeItem(i)
                continue
            myItem = editListItem(itemWidget.caption, itemWidget.imagePath, itemWidget.link, item, self)
            self.elements.feedList.setItemWidget(item, myItem)
            i += 1

    def iterateFeedWidgets(self):
        for i in range(self.elements.feedList.count()):
            yield self.elements.feedList.itemWidget(self.elements.feedList.item(i))

    def iterateFeedItems(self):
        for i in range(self.elements.feedList.count()):
            yield self.elements.feedList.item(i)

    def resizeEvent(self, event):
        self.elements.gagLabel.adjust()

    def closeEvent(self, event):
        self.exiting = True
        event.accept()