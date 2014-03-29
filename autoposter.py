__author__ = 'Alexander'

period = 3600 # период постинга, в секундах!
groupname = 'ru9gag' # название группы в которую постить!
count = 1 # сколько новостей постить за раз
post_type = 'album' # как постить
# album - через альбом на стену
# wall now - сразу на стену
# wall delay - в отложенные записи
delay = 3600 # на сколько откладывать пост, в секундах (учитывается при post_type = wall_delay

from PyQt4 import QtCore, QtGui
from libs.gorokhovlibs.vk import accesstokener
from libs.gorokhovlibs.vk.api import VKApi
from libs.gorokhovlibs.threading import threaded
from libs import constants, vkpost
from libs.gagapi import Gag_api
from resourses import resourcefile

import time, os, time

if not accesstokener.good():
    from libs.gorokhovlibs.vk.qt.auth import show_browser

    access_token, user_id, expires = show_browser(constants.application_id, constants.permissions_scope)
    accesstokener.new(access_token, user_id, expires)
else:
    access_token, user_id, expires = accesstokener.get()

api = VKApi(access_token)


class Trayer(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.createActions()
        self.createTray()
        self.exiting = self.interrupt = False
        self.connect(self, QtCore.SIGNAL("showMessage(QString, QString, int)"), self.__showMessage)
        self.showMessage = lambda title, msg, t: self.emit(QtCore.SIGNAL("showMessage(QString, QString, int)"), title,
                                                           msg, t)
        self.showMessage('9GAG Autoposter', 'Я здесь!', 1)
        self.worker()

    def createActions(self):
        self.quitAction = QtGui.QAction("Выход", self, triggered=self.quit)
        self.forseAction = QtGui.QAction("Принудительно", self, triggered=self.interr)

    def interr(self):
        self.interrupt = True

    def waiter(self):
        for i in range(period):
            time.sleep(1)
            if self.exiting:
                return
            if self.interrupt:
                self.interrupt = False
                return

    def post(self, news):
        imagePath = api.download(news['images']['large'])
        os.rename(imagePath, imagePath + '.jpeg')
        imagePath += '.jpeg'
        if post_type == 'album':
            aid = vkpost.get_album(api, constants.groups[groupname])
            vkpost.album_post(api, constants.groups[groupname], aid, news["caption"], news["link"], imagePath)
        elif post_type == 'wall now':
            vkpost.wall_post_now(api, constants.groups[groupname], news["caption"], news["link"], imagePath)
        elif post_type == 'wall delay':
            vkpost.wall_post_later(api, constants.groups[groupname], news["caption"], news["link"], imagePath,
                                   time.time() + delay)

    @threaded
    def worker(self):
        while not self.exiting:
            self.waiter()
            self.showMessage('9GAG Autoposter', 'Получаю новости', 1)
            try:
                feed = Gag_api().call('hot')["data"][:count]
                for news in feed:
                    if self.exiting: return
                    self.post(news)
            except Exception as e:
                print(e)
                self.showMessage('9GAG Autoposter', str(e), 3)
                continue
            else:
                self.showMessage('9GAG Autoposter', 'Отработал, жду', 1)

    def createTray(self):
        self.trayMenu = QtGui.QMenu(self)
        self.trayMenu.addAction(self.forseAction)
        self.trayMenu.addSeparator()
        self.trayMenu.addAction(self.quitAction)
        self.trayIcon = QtGui.QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayMenu)
        self.trayIcon.setIcon(QtGui.QIcon(QtGui.QPixmap(':/Icons/icon.png')))
        self.trayIcon.show()

    def __showMessage(self, title, message, t):
        self.trayIcon.showMessage(title,
                                  message, t, 5)

    def quit(self):
        self.exiting = True
        QtGui.qApp.quit()


app = QtGui.QApplication([])
QtGui.QApplication.setQuitOnLastWindowClosed(False)
tray = Trayer()
exit(app.exec_())
