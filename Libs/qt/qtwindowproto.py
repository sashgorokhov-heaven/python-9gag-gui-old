from PyQt4 import QtGui, uic


class Elements:
    def __init__(self, treedict):
        self._setnames(treedict)

    def _setnames(self, treedict):
        for key in treedict:
            if isinstance(treedict[key], dict):
                if 'self' in treedict[key]:
                    setattr(self, key, treedict[key]['self'])
                self._setnames(treedict[key])


class WindowProto(QtGui.QWidget):
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
                childs[child.objectName()] = WindowProto._set_childs(self, child)
            return childs
        return {'self': parent}

    def _set_connections(self):
        raise NotImplementedError

    def _set_elements(self, attrname, childs):
        setattr(self, attrname, Elements(childs))


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
                childs[child.objectName()] = WindowProto._set_childs(self, child)
            return childs
        return {'self': parent}

    def _set_connections(self):
        raise NotImplementedError

    def _set_elements(self, attrname, childs):
        setattr(self, attrname, Elements(childs))


if __name__ == '__main__':
    # How to use WindowProto class

    class YourWindow(WindowProto):
        def __init__(self):
            super().__init__(self, 'YourWindow.ui')

        def _set_connections(self):
            self.elements.Button1.clicked.connect(lambda: print(self.elements.Label1.text()))
