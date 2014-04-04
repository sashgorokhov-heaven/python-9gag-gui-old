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
        self.elements.postLabel.setVisible(False)
        self.elements.postLabel.movie = QtGui.QMovie(':/Icons/ajax-loader.gif')
        self.elements.postLabel.setMovie(self.elements.postLabel.movie)
        self.feedList = FeedList(self.elements.feedList, self)
        self.editList = EditList(self.elements.editList, self, access_token, self.feedList.news)
        self.feedList.getFeed()

    def _set_connections(self):
        self.connect(self, QtCore.SIGNAL("feed_loading(bool)"), self.__feed_loading)
        self.connect(self, QtCore.SIGNAL("edit_posting(bool)"), self.__edit_posting)

    def __feed_loading(self, state):
        if state:
            self.elements.refreshButton.setEnabled(False)
            self.elements.sendButton.setEnabled(False)
            self.elements.reloadLabel.setVisible(True)
            self.elements.reloadLabel.movie.start()
        else:
            self.elements.refreshButton.setEnabled(True)
            self.elements.sendButton.setEnabled(True)
            self.elements.reloadLabel.setVisible(False)
            self.elements.reloadLabel.movie.stop()

    def feed_loading(self, state):
        self.emit(QtCore.SIGNAL("feed_loading(bool)"), state)

    def __edit_posting(self, state):
        if state:
            self.elements.sendButton.setEnabled(False)
            self.elements.refreshButton.setEnabled(False)
            self.elements.postLabel.setVisible(True)
            self.elements.postLabel.movie.start()
        else:
            self.elements.sendButton.setEnabled(True)
            self.elements.refreshButton.setEnabled(True)
            self.elements.postLabel.setVisible(False)
            self.elements.postLabel.movie.stop()

    def edit_posting(self, state):
        self.emit(QtCore.SIGNAL("edit_posting(bool)"), state)

    def closeEvent(self, event):
        self.exiting = True
        event.accept()