__author__ = 'Alexander Gorokhov'

try:
    from PyQt4 import QtCore, QtWebKit, QtGui
except ImportError:
    print('PyQt4 is missing')
    input('> Press any button...')
    exit(1)
from urllib.parse import urlparse

"""\
    Special module that shows Qt window, where user can log in vkontakte and grand access for your application.
    Call method 'showBrowser' with arguments (your application id, permission scope). It works in blocking mode,
    so you wont be able to run your program until user doesn close that window or logins. On success, returns
    tuple(access token, user id) or tuple(None, None) if user closed that window.\
"""


class AuthWindow(QtWebKit.QWebView):
    def __init__(self, appId, scope):
        super().__init__()
        url = 'http://oauth.vk.com/oauth/authorize?' + \
              'redirect_uri=oauth.vk.com/blank.html&' + \
              'response_type=token&' + \
              'client_id={0}&scope={1}&'.format(appId,
                                                ','.join(scope)) + \
              'display=wap'
        self.accessToken = None
        self.userId = None
        self.urlChanged.connect(self.webUrlChanged)
        self.load(QtCore.QUrl(url))

    def webUrlChanged(self, newUrl):
        url = newUrl.toString()
        if urlparse(url).path != '/blank.html':
            return
        params = {
            p_pair.split('=')[0]: p_pair.split('=')[1]
            for p_pair in url.split('#')[1].split('&')}
        self.accessToken = params['access_token']
        self.userId = params['user_id']
        self.close()


def showBrowser(appId, scope):
    app = QtGui.QApplication([])
    form = AuthWindow(appId, scope)
    form.show()
    app.exec_()
    return form.accessToken, form.userId

