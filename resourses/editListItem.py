__author__ = 'Alexander'
from resourses.feedListItem import GroupBoxProto
from PyQt4 import QtGui, QtCore
from os import sep


class editListItem(GroupBoxProto):
    def __init__(self, nid, parentItem, parent):
        super().__init__(self, "resourses" + sep + "editListItem.ui")
        self.id = nid
        self.news = parent.feed.news[nid]
        self.news['editwidget'] = self
        self.setCaption(self.news['caption'])
        self.parent = parent
        self.parentItem = parentItem
        self.parentItem.setSizeHint(self.sizeHint())
        self.setImage(self.news['path'])
        self.elements.dateTimeEdit.setTime(QtCore.QTime.currentTime())
        self.elements.dateTimeEdit.setDate(QtCore.QDate.currentDate())

    def _set_connections(self):
        self.elements.waitUntilCheckBox.stateChanged.connect(self.setDateTimeEditEnabled)
        self.elements.directWallRB.toggled.connect(self.setwaitUntilCheckBoxEnabled)

    def setwaitUntilCheckBoxEnabled(self, checkState):
        if checkState:
            self.elements.waitUntilCheckBox.setEnabled(True)
        else:
            self.elements.waitUntilCheckBox.setEnabled(False)
            self.setDateTimeEditEnabled(0)

    def setDateTimeEditEnabled(self, checkState):
        if checkState == 2:
            self.elements.dateTimeEdit.setEnabled(True)
            self.elements.dateTimeEdit.setTime(QtCore.QTime.currentTime())
            self.elements.dateTimeEdit.setDate(QtCore.QDate.currentDate())
        else:
            self.elements.dateTimeEdit.setEnabled(False)

    def setCaption(self, caption):
        self.elements.captionLabel.setText(str(caption))

    def setImage(self, imagePath):
        self.elements.imageLabel.setText("")
        width = 400
        pixmap = QtGui.QPixmap(imagePath).scaledToWidth(width)
        self.elements.imageLabel.resize(pixmap.width(), pixmap.height())
        self.elements.imageLabel.setPixmap(pixmap)
        self.parentItem.setSizeHint(self.sizeHint())

    def checked(self):
        return self.elements.checkBox.isChecked()