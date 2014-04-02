__author__ = 'Александр Горохов'

from PyQt4 import QtGui, QtCore
from libs.listitems import FeedListItemWidget, EditListItemWidget
#from resourses.editListItem import editListItem
import threading, time, sys, os
from libs.gagapi import GagApi
from libs.gorokhovlibs.vk.api import VKApi
from libs.gorokhovlibs.threadeddecor import threaded


class FeedList(QtCore.QObject):
    def __init__(self, qlistwidget, parent):
        super().__init__()
        self.parent = parent
        self.qtlist = qlistwidget
        self.api = GagApi()
        self.nextPage = 0
        self.complete = False
        self.loading = False
        self.addingLock = threading.Lock()
        self.news = dict()
        self.loadQueque = list()
        self.connect(self, QtCore.SIGNAL("addFeedItem(QString)"), self.__addItem)
        self.connect(self, QtCore.SIGNAL("setFeedProgressBar(int)"), self.parent.elements.feedProgressBar.setValue)
        self.connect(self, QtCore.SIGNAL("item_toggled(QString)"), self.item_toggled)
        self.parent.refreshButton.clicked.connect(self.refresh)
        self.setProgressBar(0)
        self.qtlist.verticalScrollBar().valueChanged.connect(self.handle_scrollBarValue)

    def item_toggled(self, nid):
        pass

    def setProgressBar(self, n):
        self.emit(QtCore.SIGNAL("setFeedProgressBar(int)"), int(n))

    def __addItem(self, nid):
        with self.addingLock:
            item = QtGui.QListWidgetItem()
            widget = FeedListItemWidget(nid, self.news[nid], item, self)
            self.qtlist.addItem(item)
            self.qtlist.setItemWidget(item, widget)
            if 'path' not in self.news[nid]:
                self.loadQueque.append(nid)

    def addItem(self, nid):
        self.emit(QtCore.SIGNAL("addFeedItem(QString)"), str(nid))
        self.addingLock.acquire()
        self.addingLock.release()

    def refresh(self):
        self.qtlist.clear()
        for nid in self.news:
            self.news[nid].pop("feeditem", False)
            self.news[nid].pop("feedwidget", False)
        self.nextPage = 0
        self.getFeed()

    @threaded
    def getFeed(self, section='hot', pid=None):
        self.loading = True
        self.complete = False
        if not pid: pid = self.nextPage
        self.parent.feed_loading(True)
        gagfeed = None
        while True:
            if self.parent.exiting:
                return
            try:
                gagfeed = self.api.call(section, pid)
            except Exception as e:
                print('Error - cant get news from 9GAG')
                print(e)
                sys.stdout.flush()
                time.sleep(3)
            else:
                if "data" not in gagfeed or not gagfeed["data"]:
                    print("Empty GAG data")
                    continue
                break

        self.nextPage = gagfeed["paging"]["next"]
        gagfeed = gagfeed["data"]
        self.loadImages()
        self.newitemscount = len(gagfeed)
        for newsitem in gagfeed:
            if self.parent.exiting:
                return
            if str(newsitem['id']) not in self.news:
                self.news[str(newsitem['id'])] = {'title': newsitem["caption"],
                                                  'votes': str(newsitem["votes"]["count"]),
                                                  'link': newsitem['link'],
                                                  'image': newsitem["images"]["large"],
                                                  'posted': False}
            self.addItem(str(newsitem['id']))
        self.complete = True

    @threaded
    def loadImages(self):
        n = 0
        self.setProgressBar(n)
        while not self.complete:
            time.sleep(0.1)
            while len(self.loadQueque) > 0:
                nid = self.loadQueque.pop(0)
                imagePath = None
                for i in range(2):
                    if self.parent.exiting:
                        return
                    try:
                        imagePath = self.api.download(self.news[nid]['image'])
                        os.rename(imagePath, imagePath + '.jpg')
                        imagePath += '.jpg'
                    except Exception as e:
                        print('Error while loading image for caption "{}" {} time'.format(self.news[nid]['caption'], i))
                        continue
                    else:
                        break
                if not imagePath:
                    self.loadQueque.append(nid)
                    continue
                n += 1
                self.news[nid]['imagepath'] = imagePath
                self.news[nid]['feedwidget'].setImage()
                self.setProgressBar(round((n / self.newitemscount) * 100))
        self.setProgressBar(100)
        self.loading = False
        self.parent.feed_loading(False)

    def __iter__(self):
        return [(self.qtlist.item(i), self.qtlist.itemWidget(self.qtlist.item(i)))
                for i in range(self.qtlist.count())].__iter__()

    def __len__(self):
        return self.qtlist.count()

    def handle_scrollBarValue(self, value):
        scrollbar = self.qtlist.verticalScrollBar()
        if value != scrollbar.maximum(): return
        if not self.loading:
            self.getFeed()


class EditList(QtCore.QObject):
    def __init__(self, qlistwidget, parent, acctoken, news):
        super().__init__()
        self.qtlist = qlistwidget
        self.news = news
        self.parent = parent
        self.api = VKApi(acctoken)
        self.posting = False
        self.connect(self, QtCore.SIGNAL("addEditItem(QString)"), self.__addItem)
        self.connect(self, QtCore.SIGNAL("setEditProgressBar(int)"), self.parent.elements.editProgressBar.setValue)

    def setProgressBar(self, n):
        self.emit(QtCore.SIGNAL("setEditProgressBar(int)"), int(n))

    def __addItem(self, nid):
        item = QtGui.QListWidgetItem()
        widget = EditListItemWidget(nid, self.news[nid], item, self)
        self.qtlist.addItem(item)
        self.qtlist.setItemWidget(item, widget)

    def addItem(self, nid):
        self.emit(QtCore.SIGNAL("addEditItem(QString)"), str(nid))

    def __iter__(self):
        return [(self.qtlist.item(i), self.qtlist.itemWidget(self.qtlist.item(i)))
                for i in range(self.qtlist.count())].__iter__()

    def __len__(self):
        return self.qtlist.count()

    def clear(self):
        self.qtlist.clear()
        for nid in self.parent.feedList.news:
            self.parent.feedList.news[nid].pop("edititem", False)
            self.parent.feedList.news[nid].pop("editwidget", False)