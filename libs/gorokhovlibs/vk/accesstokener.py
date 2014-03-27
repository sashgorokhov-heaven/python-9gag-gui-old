__author__ = 'Alexander'

import os.path, datetime, time

__filename = 'actk'
__tformat = '%Y-%m-%d %H:%M:%S'


def good():
    if os.path.exists(__filename):
        with open(__filename, 'r') as f:
            token, uid, expires = f.readline().strip().split(' ')
            dt = time.mktime(time.strptime(f.readline().strip(), __tformat))
            if int(time.time()) - int(dt) < int(expires):
                return True
    return False


def get():
    with open(__filename, 'r') as f:
        return f.readline().strip().split(' ')


def new(token, userid, expires):
    with open(__filename, 'w') as f:
        f.write(' '.join([token, userid, expires]) + '\n')
        f.write(time.strftime(__tformat))
