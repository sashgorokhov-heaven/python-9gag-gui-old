__author__ = 'Alexander'

from libs.gorokhovlibs.vk import accesstokener
from libs.gorokhovlibs.vk.api import VKApi
from libs import constants

print('\nAuthorising... ', end='')
if not accesstokener.good():
    from libs.gorokhovlibs.vk.qt.auth import show_browser

    access_token, user_id, expires = show_browser(constants.application_id, constants.permissions_scope)
    accesstokener.new(access_token, user_id, expires)
else:
    access_token, user_id, expires = accesstokener.get()
print('Yup.')

api = VKApi(access_token)

print('\nChoose your destiny: ')
choosedict = dict()
for n, group in enumerate(constants.groups, 1):
    print('{} - {}'.format(n, group))
    choosedict[n] = group
n = int(input('Your choice: '))
print('\n{}? Good choice...'.format(choosedict[n]))
group = constants.groups[choosedict[n]]

print('\nGetting first 100 news for {} ... '.format(choosedict[n]), end='')
wall = api.call('wall.get', owner_id='-' + group, count='100')['items']
print('OK.')

print("\nWalking through news and smokin' cuban cigar...")
k = list()
for n, post in enumerate(wall):
    if not 'attachments' in post: continue
    link = [i['link']['url'] for i in post['attachments'] if i['type'] == 'link']
    if len(link) > 0:
        postset = {attach['link']['url'] for item in wall[n + 1:] if 'attachments' in item for attach in
                   item['attachments'] if attach['type'] == 'link'}
        if link[0] in postset:
            k.append(post['id'])
            print('Found {} identical news!'.format(len(k)))

if len(k) == 0:
    print("It was perfect stroll, bye!")
    exit(1)

print('\nUnfortunately i have to delete {} news! '.format(len(k)), end='')
for pid in k:
    api.call('wall.delete', owner_id='-' + group, post_id=str(pid))
print('Done.\nBye!')

