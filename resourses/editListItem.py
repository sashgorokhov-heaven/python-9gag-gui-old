__author__ = 'Alexander'
from resourses.feedListItem import GroupBoxProto
from PyQt4 import QtGui, QtCore
from os import sep


class editListItem(GroupBoxProto):
    def __init__(self, caption, imagePath, link, holdingItem, window):
        super().__init__(self, "resourses" + sep + "editListItem.ui")
        self.caption = ""
        self.setCaption(caption)
        self.window = window
        self.link = link
        self.posttime = None
        self.imagePath = imagePath
        self.holdingItem = holdingItem
        self.holdingItem.setSizeHint(self.sizeHint())
        self.setImage(self.imagePath)
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
        self.caption = caption

    def setImage(self, imagePath):
        self.elements.imageLabel.setText("")
        width = 400
        pixmap = QtGui.QPixmap(imagePath).scaledToWidth(width)
        self.elements.imageLabel.resize(pixmap.width(), pixmap.height())
        self.elements.imageLabel.setPixmap(pixmap.scaledToWidth(width))
        self.holdingItem.setSizeHint(self.sizeHint())

    def checked(self):
        return self.elements.checkBox.isChecked()