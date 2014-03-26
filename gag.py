__author__ = 'Alexander'

from libs import constants, util

try:
    import requests
except ImportError:
    print("Module 'requests' is not found")
    exit(-1)
try:
    import PyQt4
except ImportError:
    print("Module 'PyQt4' is not found")
    exit(-1)

login = ""
password = ""

access_token = user_id = None

if not login or not password:
    from libs.gorokhovlibs.vk.qt.auth import show_browser

    access_token, user_id = show_browser(constants.application_id, constants.permissions_scope)
elif login and password:
    from libs.gorokhovlibs.vk.auth import VKAuth

    access_token, user_id = VKAuth(login, password,
                                   constants.application_id, constants.permissions_scope).result()
if not access_token:
    util.showmessage("Didn't get secret key!")
    exit(-1)

from forms.main_form import MainForm

app = PyQt4.QtGui.QApplication([])
mainform = MainForm(access_token)
mainform.show()
app.exec_()
