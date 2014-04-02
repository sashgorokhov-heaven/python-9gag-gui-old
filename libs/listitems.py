__author__ = 'sashgorokhov'
__email__ = 'sashgorokhov@gmail.com'

from PyQt4 import uic, QtGui, QtCore
from libs.gorokhovlibs.qt import qtwindow
from resourses import resourcefile
import os


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


class FeedListItemWidget(GroupBoxProto):
    def __init__(self, nid, news, parentitem, parent):
        super().__init__(self, "resourses" + os.sep + "FeedListItem.ui")
        self.nid = nid
        self.news = news
        self.news['feedwidget'] = self
        self.setInfo(news['title'], news['votes'], news['link'])
        self.imageLoaded = False
        self.imageHidden = False
        self.parent = parent
        self.parentItem = parentitem
        self.elements.imageLabel.movie = QtGui.QMovie(":/Icons/preloader.gif")
        self.elements.hideButton.setEnabled(False)
        self.elements.hideButton2.setEnabled(False)
        self.parentItem.setSizeHint(self.sizeHint())
        if 'imagepath' not in news:
            self.setLoading()
        else:
            self.setImage()
        if news['posted']:
            self.setPosted()

    def _set_connections(self):
        self.connect(self, QtCore.SIGNAL("setImage()"), self.__setImage)
        self.connect(self, QtCore.SIGNAL("setLoading()"), self.__setLoading)
        self.connect(self, QtCore.SIGNAL("setError()"), self.__setError)
        self.connect(self, QtCore.SIGNAL("setPosted()"), self.__setPosted)
        self.connect(self, QtCore.SIGNAL("setMessage(QString)"), self.__setMessage)
        self.elements.checkBox.stateChanged.connect(self.setChecked)
        self.elements.hideButton.clicked.connect(self.hideButtonClicked)
        self.elements.hideButton2.clicked.connect(self.hideButtonClicked)
        self.elements.imageLabel.mouseDoubleClickEvent = self.imageDoubleClicked
        self.elements.linkLabel.mouseDoubleClickEvent = self.linkDoubleClicked

    def hideButtonClicked(self):
        pass

    def setMessage(self, msg):
        self.emit(QtCore.SIGNAL("setMessage(QString)"), str(msg))

    def __setMessage(self, msg):
        self.elements.imageLabel.clear()
        self.elements.imageLabel.setText(msg)

    def setImage(self):
        self.emit(QtCore.SIGNAL("setImage()"))

    def __setImage(self):
        self.elements.imageLabel.movie.stop()
        self.elements.imageLabel.setText("")
        pixmap = QtGui.QPixmap(self.news['imagepath']).scaledToWidth(self.elements.imageLabel.width())
        self.elements.imageLabel.setPixmap(pixmap)
        self.elements.imageLabel.resize(pixmap.width(), pixmap.height())
        self.parentItem.setSizeHint(self.sizeHint())
        self.elements.imageLabel.resize(pixmap.width(), pixmap.height())
        self.elements.hideButton.setEnabled(True)
        self.elements.hideButton2.setEnabled(True)
        self.imageLoaded = True

    def setPosted(self):
        self.emit(QtCore.SIGNAL("setPosted()"))

    def __setPosted(self):
        self.setChecked(0)
        self.setStyleSheet("background-color: rgb(50, 50, 50);")
        self.setEnabled(False)

    def setInfo(self, title, votes, link):
        self.elements.titleLabel.setText(str(title))
        self.elements.votesLabel.setText(str(votes))
        self.elements.linkLabel.setText(str(link))

    def setChecked(self, checkState):
        if not self.imageLoaded or self.news['posted']: return
        if checkState == 2:
            self.setStyleSheet("background-color: rgb(161, 255, 144);")
        else:
            self.setStyleSheet("")
        self.parent.parent.emit(QtCore.SIGNAL("item_toggled(QString)"), self.nid)

    def mouseDoubleClickEvent(self, event):
        if not self.imageLoaded: return
        if self.checked():
            self.elements.checkBox.setCheckState(0)
        else:
            self.elements.checkBox.setCheckState(2)

    def imageDoubleClicked(self, event):
        if self.imageLoaded:
            os.startfile(self.news['imagepath'])

    def linkDoubleClicked(self, event):
        os.startfile(self.elements.linkLabel.text())

    def setLoading(self):
        self.emit(QtCore.SIGNAL("setLoading()"))

    def __setLoading(self):
        self.elements.imageLabel.setMovie(self.elements.imageLabel.movie)
        self.elements.imageLabel.movie.start()

    def setError(self):
        self.emit(QtCore.SIGNAL("setError()"))

    def __setError(self):
        self.elements.imageLabel.movie.stop()
        self.elements.imageLabel.setPixmap(QtGui.QPixmap(":/Icons/error-icon.png"))

    def checked(self):
        return self.elements.checkBox.isChecked() and not self.news['posted']