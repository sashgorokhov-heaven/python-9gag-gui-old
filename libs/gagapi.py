__author__ = 'Alexander'

import json
import urllib.request


class GagApi():
    apiserver = "http://infinigag-us.aws.af.cm/"

    def __init__(self):
        self.sections = {'trending', 'hot', 'vote', 'fresh'}

    def call(self, section, id=0):
        if section not in self.sections:
            raise AttributeError("Invalid section: ".format(section))
        return self._send(section, str(id))

    def _send(self, section, id):
        url = '{0}/{1}/{2}'.format(self.apiserver, section, id)
        response = urllib.request.urlopen(url).read()
        return json.loads(response.decode())

    def download(self, link, filename=''):
        if filename:
            urllib.request.urlretrieve(link, filename)
            return filename
        else:
            return urllib.request.urlretrieve(link)[0]
