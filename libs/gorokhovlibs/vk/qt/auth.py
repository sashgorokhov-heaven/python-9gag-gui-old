from PyQt4 import QtCore, QtGui, QtWebKit
from urllib.parse import urlparse


class __QtAuthWindow(QtWebKit.QWebView):
    def __init__(self, appId, scope):
        super().__init__()
        url = 'http://oauth.vk.com/oauth/authorize?' + \
              'redirect_uri=oauth.vk.com/blank.html&' + \
              'response_type=token&' + \
              'client_id={0}&scope={1}&'.format(appId,
                                                ','.join(scope)) + \
              'display=wap&revoke=1'
        self.accessToken = None
        self.userId = None
        self.expires = None
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
        self.expires = params['expires_in']
        self.close()


def show_browser(appId, scope):
    app = QtGui.QApplication([])
    form = __QtAuthWindow(appId, scope)
    form.show()
    app.exec_()
    return form.accessToken, form.userId, form.expires
