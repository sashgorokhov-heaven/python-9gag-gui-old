__author__ = 'Alexander'
from PyQt4 import QtCore, QtGui
from os import sep

from libs.gorokhovlibs.qt.qtwindow import BaseQtWindow
from libs.lists import *


class MainForm(BaseQtWindow):
    def __init__(self, access_token):
        self.exiting = False
        super().__init__(self, 'resourses' + sep + 'MainForm.ui')
        self.elements.reloadLabel.setVisible(False)
        self.elements.reloadLabel.movie = QtGui.QMovie(':/Icons/ajax-loader.gif')
        self.elements.reloadLabel.setMovie(self.elements.reloadLabel.movie)
        self.feedList = FeedList(self.elements.feedList, self)
        self.editList = EditList(self.elements.editList, self, access_token, self.feedList.news)
        self.feedList.getFeed()

    def _set_connections(self):
        self.connect(self, QtCore.SIGNAL("feed_loading(bool)"), self.__feed_loading)
        self.connect(self, QtCore.SIGNAL("edit_posting(bool)"), self.__edit_posting)

    # @threaded
    # def post(self):
    #     for n, item in enumerate(self.iterateEditItems()):
    #         if self.exiting:
    #             return
    #         widget = self.elements.editList.itemWidget(item)
    #         self.emit(QtCore.SIGNAL("setStyleSheet(QString, int)"), "background-color: rgb(148, 205, 255)", n)
    #         try:
    #             vkpost.post(self.api, self.feed.news[widget.id])
    #         except Exception as e:
    #             showmessage('Error while posting: ' + str(e))
    #             self.emit(QtCore.SIGNAL("setStyleSheet(QString, int)"), "background-color: rgb(255, 117, 112)", n)
    #             continue
    #         self.emit(QtCore.SIGNAL("setStyleSheet(QString, int)"), "background-color: rgb(161, 255, 144)", n)
    #         self.feed.news[widget.id]['posted'] = True
    #         self.feed.news[widget.id]['feedwidget'].setPosted()
    #         self.elements.countLabel.dec()
    #     self.elements.nextButton.setEnabled(True)

    # def nextButtonClicked(self):
    #     if self.mode == 'feed':
    #         self.mode = 'editing'
    #         self.elements.nextButton.setText("Загрузить!")
    #         for widget in self.iterateFeedWidgets():
    #             if widget.checked():
    #                 item = QtGui.QListWidgetItem()
    #                 myItem = editListItem(widget.id, item, self)
    #                 self.elements.editList.addItem(item)
    #                 self.elements.editList.setItemWidget(item, myItem)
    #         self.stackedWidget.setCurrentIndex(1)
    #         self.elements.nextButton.setEnabled(True)
    #         return
    #     if self.mode == 'editing':
    #         self.elements.nextButton.setEnabled(False)
    #         self.post()
    #         self.elements.nextButton.setText("<- Назад")
    #         self.mode = 'back'
    #         return
    #     if self.mode == 'back':
    #         self.elements.nextButton.setEnabled(False)
    #         self.elements.nextButton.setText("-> Далее")
    #         self.mode = 'feed'
    #         self.elements.editList.clear()
    #         self.elements.stackedWidget.setCurrentIndex(0)

    def __feed_loading(self, state):
        if state:
            self.elements.refreshButton.setEnabled(False)
            self.elements.reloadLabel.setVisible(True)
            self.elements.reloadLabel.movie.start()
        else:
            self.elements.refreshButton.setEnabled(True)
            self.elements.reloadLabel.setVisible(False)
            self.elements.reloadLabel.movie.stop()

    def feed_loading(self, bool):
        self.emit(QtCore.SIGNAL("feed_loading(bool)"), bool)

    def __edit_posting(self, state):
        pass

    def edit_posting(self, bool):
        self.emit(QtCore.SIGNAL("edit_posting(bool)"), bool)

    def closeEvent(self, event):
        self.exiting = True
        event.accept()