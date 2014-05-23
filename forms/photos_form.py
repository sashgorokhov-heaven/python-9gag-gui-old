__author__ = 'sashgorokhov'
__email__ = 'sashgorokhov@gmail.com'

from PyQt4 import QtCore, QtGui, Qt
from os import sep

import time, threading

from libs.gorokhovlibs.vk.api import VKApi
from libs.gorokhovlibs.threadeddecor import threaded
from libs.gorokhovlibs.qt.qtwindow import BaseQtWindow


class PhotosForm(BaseQtWindow):
    def __init__(self, api, gid, aid):
        self.k = 100
        super().__init__(self, 'resourses' + sep + 'PhotosForm.ui')
        self.api = VKApi(api)
        self.set_photos(gid, aid)
        self.stop = False
        self.stopload = False
        self.photos = None
        a = 3
        self.updating = False
        self.addingLock = threading.Lock()

    def _set_connections(self):
        self.elements.koefSlider.valueChanged.connect(self.koefSliderValueChanged)
        self.connect(self, QtCore.SIGNAL("addItem(int)"), self.__addItem)
        self.connect(self, QtCore.SIGNAL("updateTone(int)"), self.__updateTone)

    def koefSliderValueChanged(self, value):
        self.k = int(value)
        if self.updating:
            self.stop = True
        self.updateTones()

    @threaded
    def updateTones(self):
        self.updating = True
        for i in self.iteratePhotos():
            if self.stop:
                break
            self.updateTone(i.pid)
        self.stop = False
        self.updating = False


    def __updateTone(self, pid, item=None):
        rate = self.get_rate(int(self.photos[pid]['likes']['count']),
                             int(self.photos[pid]['comments']['count']),
                             self.get_time_diff(self.photos[pid]['date']))
        tone = self.get_tone(rate)
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor(*self.toner(tone)))
        brush.setStyle(1)
        if item:
            item.setBackground(brush)
        else:
            self.elements.photosList.item(pid).setBackground(brush)

    def __addItem(self, pid):
        with self.addingLock:
            label = '{}\n{}'.format(self.photos[pid]['likes']['count'], self.photos[pid]['comments']['count'])
            item = QtGui.QListWidgetItem(QtGui.QIcon(self.photos[pid]['path']), label)
            item.pid = pid
            self.__updateTone(pid, item)
            self.elements.photosList.addItem(item)

    def iteratePhotos(self):
        return [self.elements.photosList.item(i) for i in range(self.elements.photosList.count())].__iter__()


    def updateTone(self, pid):
        self.emit(QtCore.SIGNAL("updateTone(int)"), pid)

    def addItem(self, pid):
        self.emit(QtCore.SIGNAL("addItem(int)"), pid)


    @threaded
    def set_photos(self, gid, aid):
        self.photos = self.api.call("photos.get", owner_id=gid, album_id=aid, extended='1', rev='1')['items']
        self.elements.countLabel.setText(str(len(self.photos)))
        for n, photo in enumerate(self.photos):
            if self.stopload: break
            self.photos[n]['path'] = self.api.download(photo['photo_75'])
            self.addingLock.acquire()
            self.addingLock.release()
            self.addItem(n)

    def get_time_diff(self, unixtime):
        return round((time.time() - int(unixtime)) / 60)

    def get_tone(self, rate):
        if rate >= 60:
            tone = 60
        else:
            tone = round(rate)
        return tone

    def toner(self, tone):
        toyellow = [(222, x, 0) for x in range(0, 222, 6)]
        togreen = [(x, 222, 0) for x in range(222, 0, -6)]
        all = toyellow
        for i in togreen:
            all.append(i)
        return all[tone]

    def get_rate(self, likes, comments, timepassed):
        return ((int(likes) + int(comments) * 2) / int(timepassed)) * self.k


    def closeEvent(self, event):
        self.stop = True
        self.stopload = True
        event.accept()