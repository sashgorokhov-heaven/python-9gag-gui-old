__author__ = 'Alexander'

# TODO: Скрипт удаления одинаковых новостей
# TODO: Скрипт-сервис автопоста

from libs import constants, util
from libs.gorokhovlibs.vk import accesstokener

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

if not accesstokener.good():
    if not login or not password:
        from libs.gorokhovlibs.vk.qt.auth import show_browser

        access_token, user_id, expires = show_browser(constants.application_id, constants.permissions_scope)
    elif login and password:
        from libs.gorokhovlibs.vk.auth import VKAuth

        access_token, user_id, expires = VKAuth(login, password,
                                                constants.application_id, constants.permissions_scope).result()
    accesstokener.new(access_token, user_id, expires)
else:
    access_token, user_id, expires = accesstokener.get()

if not access_token:
    util.showmessage("Didn't get secret key!")
    exit(-1)

from forms.main_form import MainForm

app = PyQt4.QtGui.QApplication([])
mainform = MainForm(access_token)
mainform.show()
app.exec_()
