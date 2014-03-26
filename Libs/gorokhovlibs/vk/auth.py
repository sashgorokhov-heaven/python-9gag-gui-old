import http.cookiejar, urllib.request, urllib.parse, html.parser

# http://habrahabr.ru/post/143972/
# модуль был написан на основе данной статьи

class VKAuthError(Exception): pass


class __FormParser(html.parser.HTMLParser):
    def __init__(self):
        html.parser.HTMLParser.__init__(self)
        self.url = None
        self.params = {}
        self.in_form = False
        self.form_parsed = False
        self.method = 'GET'

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == 'form':
            if self.form_parsed:
                raise VKAuthError('Second form on page')
            if self.in_form:
                raise VKAuthError('Already in form')
            self.in_form = True
        if not self.in_form:
            return
        attrs = dict((name.lower(), value) for name, value in attrs)
        if tag == 'form':
            self.url = attrs['action']
            if 'method' in attrs:
                self.method = attrs['method']
        elif tag == 'input' and 'type' in attrs and 'name' in attrs:
            if attrs['type'] in ['hidden', 'text', 'password']:
                self.params[attrs['name']] = attrs['value'] if 'value' in attrs else ''

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == 'form':
            if not self.in_form:
                raise VKAuthError('Unexpected end of <form>')
            self.in_form = False
            self.form_parsed = True


class VKAuth:
    def __init__(self, login, passwd, app_id, scope):
        """\
            To get access token and user id, call .result() method of created object.\
        """

        if not isinstance(scope, list):
            scope = [scope]

        self._opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
            urllib.request.HTTPRedirectHandler())

        try:
            response = self._opener.open(
                'http://oauth.vk.com/oauth/authorize?' + \
                'redirect_uri=oauth.vk.com/blank.html&response_type=token&' + \
                'client_id={0}&scope={1}&display=wap'.format(app_id, ','.join(scope))
            )
        except urllib.error.URLError as e:
            raise VKAuthError('Cant connect to vk.com or app_id is invalid.')
        except Exception as e:
            raise VKAuthError('Unhandled exception: ' + str(e))

        doc = response.read().decode()
        parser = __FormParser()
        parser.feed(doc)
        parser.close()

        if not parser.form_parsed or parser.url is None or 'pass' not in parser.params or 'email' not in parser.params:
            raise VKAuthError('Unexpected response page o_O')

        parser.params['email'] = login
        parser.params['pass'] = passwd
        parser.method = 'POST'
        keys = [i for i in parser.params]
        for i in keys:
            b = '1'.encode()
            if type(i) != type(b):
                a = i.encode()
            else:
                a = i
            if type(parser.params[i]) != type(b):
                parser.params[a] = parser.params[i].encode()
            else:
                parser.params[a] = parser.params[i]
            parser.params.pop(i)

        response = self._opener.open(parser.url, urllib.parse.urlencode(parser.params).encode())

        doc = response.read()
        url = response.geturl()

        if urllib.parse.urlparse(url).path != '/blank.html':
            url = self._give_access(doc)

        if urllib.parse.urlparse(url).path != "/blank.html":
            raise VKAuthError('Invalid email or password')

        def split_key_value(kv_pair):
            kv = kv_pair.split('=')
            return kv[0], kv[1]

        answer = dict(split_key_value(kv_pair) for kv_pair in urllib.parse.urlparse(url).fragment.split('&'))
        if 'access_token' not in answer or 'user_id' not in answer:
            raise VKAuthError('Missing some values in answer')

        self.token = answer['access_token']
        self.user_id = answer['user_id']

    def _give_access(self, doc):
        parser = __FormParser()
        parser.feed(str(doc))
        parser.close()
        if not parser.form_parsed or parser.url is None:
            raise VKAuthError('Invalid email or password')
        if parser.method == 'post':
            response = self._opener.open(parser.url, urllib.parse.urlencode(parser.params).encode())
        else:
            raise VKAuthError('Unexpected method: ' + parser.method)
        return response.geturl()

    def result(self):
        """\
            Returns tuple(access token, user id)\
        """
        return self.token, self.user_id


if __name__ == '__main__':
    email = input('Email:')
    password = input('Password:')
    app_id = input('Application id:')
    print('Authorising...')
    vk = VKAuth(email, password, app_id, ['friends', 'photos'])
    print('Token: {0}\nUser id:{1}'.format(*vk.result()))