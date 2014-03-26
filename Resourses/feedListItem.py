__author__ = 'Alexander'
import libs.gorokhovlibs.qt.qtwindow as qtwindow
from PyQt4 import QtGui, QtCore, Qt, uic
from os import sep
import os.path, os


class GroupBoxProto(QtGui.QGroupBox):
    def __init__(self, inherits, ui):
        super().__init__()
        uic.loadUi(ui, self)
        #self.setFixedSize(self.size())

        childs = self._set_childs(inherits)
        self._set_elements('elements', childs)
        self._set_connections()

    def _set_childs(self, parent):
        if len(parent.children()) != 0:
            childs = dict()
            childs['self'] = parent
            for child in parent.children():
                childs[child.objectName()] = qtwindow.BaseQtWindow._set_childs(self, child)
            return childs
        return {'self': parent}

    def _set_connections(self):
        raise NotImplementedError

    def _set_elements(self, attrname, childs):
        setattr(self, attrname, qtwindow._Elements(childs))


class feedListItem(GroupBoxProto):
    def __init__(self, caption, imageLink, votes, link, holdingItem, window):
        super().__init__(self, "resourses" + sep + "feedListItem.ui")
        self.setCaption(caption)
        self.setVotes(votes)
        self.setLink(link)
        self.imageLoaded = False
        self.window = window
        self.imageLink = imageLink
        self.imagePath = ""
        self.holdingItem = holdingItem
        self.holdingItem.setSizeHint(self.sizeHint())
        self.elements.imageLabel.movie = QtGui.QMovie(":/Icons/preloader.gif")
        self.setLoading()

    def _set_connections(self):
        self.connect(self, QtCore.SIGNAL("setImage(QString)"), self.setImage)
        self.connect(self, QtCore.SIGNAL("setLoading()"), self.setLoading)
        self.connect(self, QtCore.SIGNAL("setError()"), self.setError)
        self.elements.checkBox.stateChanged.connect(self.setChecked)
        self.elements.imageLabel.mouseDoubleClickEvent = self.imageDoubleClicked
        self.elements.linkLabel.mouseDoubleClickEvent = self.linkDoubleClicked

    def setCaption(self, caption):
        self.elements.captionLabel.setText(str(caption))
        self.caption = caption

    def setChecked(self, checkState):
        if not self.imageLoaded: return
        if checkState == 2:
            self.setStyleSheet("background-color: rgb(161, 255, 144);")
            self.window.elements.countLabel.inc()
        else:
            self.setStyleSheet("")
            self.window.elements.countLabel.dec()

    def mouseDoubleClickEvent(self, event):
        if not self.imageLoaded: return
        if self.checked():
            self.elements.checkBox.setCheckState(0)
        else:
            self.elements.checkBox.setCheckState(2)

    def imageDoubleClicked(self, event):
        if self.imageLoaded:
            os.startfile(self.imagePath)

    def linkDoubleClicked(self, event):
        os.startfile(self.elements.linkLabel.text())

    def setImage(self, imagePath):
        self.elements.imageLabel.movie.stop()
        self.elements.imageLabel.setText("")
        width = 400 #self.elements.imageLabel.width()
        pixmap = QtGui.QPixmap(imagePath).scaledToWidth(width)
        self.elements.imageLabel.resize(pixmap.width(), pixmap.height())
        self.elements.imageLabel.setPixmap(pixmap.scaledToWidth(width))
        self.imagePath = imagePath
        self.elements.imageLabel.setText("")
        self.holdingItem.setSizeHint(self.sizeHint())
        self.imageLoaded = True

    def setLoading(self):
        self.elements.imageLabel.setMovie(self.elements.imageLabel.movie)
        self.elements.imageLabel.movie.start()

    def setError(self):
        self.elements.imageLabel.movie.stop()
        self.elements.imageLabel.setPixmap(QtGui.QPixmap(":/Icons/error-icon.png"))

    def setVotes(self, votes):
        self.elements.votesLabel.setText(str(votes))

    def setLink(self, link):
        self.elements.linkLabel.setText(str(link))
        self.link = link

    def checked(self):
        return self.elements.checkBox.isChecked()