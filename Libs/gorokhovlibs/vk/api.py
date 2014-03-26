import urllib.request, urllib.parse, requests, json


class VKError(Exception): pass


class VKApi:
    def __init__(self, access_token=None):
        self.token = access_token
        self.api_version = '5.14'

    def __compile_params(self, params_dict):
        params = list()
        for key in params_dict:
            if len(str(params_dict[key])) != 0:
                if isinstance(params_dict[key], list):
                    params.append((key, ','.join(params_dict[key])))
                else:
                    params.append((key, params_dict[key]))
        if self.token:
            params.append(("access_token", self.token))
        params.append(('v', self.api_version))
        return params

    def call(self, method, **params_dict):
        params = self.__compile_params(params_dict)

        url = 'https://api.vk.com/method/{0}?{1}'.format(method, urllib.parse.urlencode(params))
        response = urllib.request.urlopen(url).read()
        response = json.loads(response.decode())

        if 'error' in response:
            raise VKError(response['error'])
        if len(response['response']) == 0:
            raise VKError('Empty response')
        return response['response']

    def download(self, link, filename=None):
        if filename:
            urllib.request.urlretrieve(link, filename)
        else:
            return urllib.request.urlretrieve(link)[0]

    def upload(self, link, filename, res_type):
        response = requests.post(link, files={"res_type": open(filename, 'rb')}).json()
        return response
