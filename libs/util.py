import os
import threading
import urllib
from resourses.feedListItem import feedListItem

__author__ = 'Alexander'
from PyQt4 import QtGui, QtCore
from libs.gorokhovlibs.threading import threaded
import time
from libs.gagapi import Gag_api

from resourses import resourcefile


class GagLabel(QtGui.QLabel):
    def __init__(self, parent):
        self.parent = parent
        self.currentState = 'normal' # normal, loading, error
        super().__init__(parent)

        self.movieGif = QtGui.QMovie(":/Icons/rotating.gif")
        self.normalPixmap = QtGui.QPixmap(":/Icons/9gag-icon.png")
        self.errorPixmap = QtGui.QPixmap(":/Icons/error-icon.png")

        self.setPixmap(self.normalPixmap)
        self.setScaledContents(True)
        self.setMouseTracking(True)
        self.resize(100, 100)

        #self.hiding = False

        self.connect(self, QtCore.SIGNAL("hide()"), self.hide)
        #self.connect(self, QtCore.SIGNAL("setVisible(bool)"), self.setVisible)
        self.connect(self, QtCore.SIGNAL("setNormal()"), lambda: self.setPixmap(self.normalPixmap))
        self.connect(self, QtCore.SIGNAL("setError()"), lambda: self.setPixmap(self.errorPixmap))
        self.connect(self, QtCore.SIGNAL("setLoading()"), self.__setLoadingSignal)
        self.connect(self, QtCore.SIGNAL("unsetLoading()"), lambda: self.movieGif.stop())
        #self.mouseMoveEvent = lambda event: self.hide()

    def __setLoadingSignal(self):
        self.setMovie(self.movieGif)
        self.movieGif.start()

    #@threaded
    #def hide(self):
    #    if self.hiding: return
    #    self.hiding = True
    #    self.emit(QtCore.SIGNAL("setVisible(bool)"), False)
    #    time.sleep(0.5)
    #    self.emit(QtCore.SIGNAL("setVisible(bool)"), True)
    #    self.hiding = False

    def adjust(self):
        self.move(self.parent.width() - self.width() + 20,
                  self.parent.height() - self.height() + 20)

    def __setNormal(self):

        self.emit(QtCore.SIGNAL("setNormal()"))

    def __setError(self):
        self.currentState = 'normal'
        self.emit(QtCore.SIGNAL("setError()"))

    def __setLoading(self):
        self.currentState = 'normal'
        self.emit(QtCore.SIGNAL("setLoading()"))

    def __unsetLoading(self):
        self.emit(QtCore.SIGNAL("unsetLoading()"))

    def setState(self, state):
        if self.currentState == 'normal':
            if state == 'normal':
                pass
            if state == 'error':
                self.__setError()
            if state == 'loading':
                self.__setLoading()
        if self.currentState == 'error':
            if state == 'normal':
                self.__setNormal()
            if state == 'error':
                pass
            if state == 'loading':
                self.__setLoading()
        if self.currentState == 'loading':
            if state == 'normal':
                self.__unsetLoading()
                self.__setNormal()
            if state == 'error':
                self.__unsetLoading()
                self.__setError()
            if state == 'loading':
                pass
        self.currentState = state


class CountLabel():
    def __init__(self, parent, label):
        self.parent = parent
        self.label = label
        self.label.setText('0')
        self.checkedItems = 0

    def inc(self):
        self.checkedItems += 1
        self.label.setText(str(self.checkedItems))
        if not self.parent.feed.loading:
            self.parent.elements.nextButton.setEnabled(True)

    def dec(self):
        self.checkedItems -= 1
        self.label.setText(str(self.checkedItems))
        if self.checkedItems == 0:
            self.parent.elements.nextButton.setEnabled(False)


class GagFeed:
    def __init__(self, parent):
        self.parent = parent
        self.api = Gag_api()
        self.nextPage = 0
        self.complete = False
        self.loading = False
        self.addingLock = threading.Lock()
        self.news = dict()  # id
        self.loadQueque = list()

    def addItem(self, nid):
        with self.addingLock:
            item = QtGui.QListWidgetItem()
            myItem = feedListItem(nid, self.news[nid], item, self.parent)
            self.parent.elements.feedList.addItem(item)
            self.parent.elements.feedList.setItemWidget(item, myItem)
            if 'path' not in self.news[nid]:
                self.loadQueque.append(nid)

    @threaded
    def getFeed(self, section="hot", nid=None):
        self.parent.elements.nextButton.setEnabled(False)
        self.loading = True
        if not nid: nid = self.nextPage
        gagfeed = None
        while True:
            self.parent.elements.gagLabel.setState('loading')
            if self.parent.exiting:
                return
            try:
                gagfeed = self.api.call(section, nid)
            except urllib.error.URLError as e:
                time.sleep(1)
                self.parent.elements.gagLabel.setState('error')
                print('Internet connection error - cant get news from 9GAG')
                print(e)
                time.sleep(3)
            except Exception as e:
                print(e)
                self.parent.elements.gagLabel.setState('error')
                return
            else:
                break

        if not gagfeed["data"] is None:
            self.nextPage = gagfeed["paging"]["next"]
            gagfeed = gagfeed["data"]
            self.complete = False
            self.loadImages()
            for newsitem in gagfeed:
                if self.parent.exiting:
                    return
                if str(newsitem['id']) not in self.news:
                    self.news[str(newsitem['id'])] = {'caption': newsitem["caption"],
                                                      'votes': str(newsitem["votes"]["count"]),
                                                      'link': newsitem['link'],
                                                      'image': newsitem["images"]["large"],
                                                      'posted': False}
                self.parent.emit(QtCore.SIGNAL("addItem(QString)"), str(newsitem['id']))
                self.addingLock.acquire()
                self.addingLock.release()
            self.complete = True
        else:
            print('Gagfeed error: ' + str(gagfeed))

        self.parent.elements.gagLabel.setState('normal')

    @threaded
    def loadImages(self):
        while not self.complete:
            time.sleep(0.2)
            while len(self.loadQueque) > 0:
                nid = self.loadQueque.pop(0)
                imagePath = None
                for i in range(2):
                    if self.parent.exiting:
                        return
                    try:
                        imagePath = self.api.download(self.news[nid]['image'])
                        os.rename(imagePath, imagePath + '.' + self.getFileType(imagePath))
                        #print('{} is {}'.format(item.caption, self.getFileType(imagePath)))
                        imagePath += '.' + self.getFileType(imagePath)
                    except Exception as e:
                        print('Error while loading image for caption "{}" {} time'.format(self.news[nid]['caption'], i))
                        continue
                    else:
                        break
                if not imagePath:
                    continue
                self.news[nid]['path'] = imagePath
                self.news[nid]['widget'].emit(QtCore.SIGNAL("setImage()"))
        self.loadQueque.clear()
        if self.parent.elements.countLabel.checkedItems > 0:
            self.parent.elements.nextButton.setEnabled(True)
        self.loading = False

    def getFileType(self, path):
        try:
            if open(path, 'rb').read()[:6].decode() == 'GIF89a':
                return '.gif'
        except:
            return '.jpeg'


def showmessage(msg):
    print(str(msg))
    #input("> Press any button...")