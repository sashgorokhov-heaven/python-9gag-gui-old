__author__ = 'Alexander'

import requests
from libs import constants


def post(api, newsitem):
    aid = get_album(api, constants.groups['ru9gag'])
    post_type = get_post_type(newsitem['editwidget'])
    if post_type == 'wall delay':
        delay = newsitem['widget'].elements.dateTimeEdit.dateTime().toTime_t()
        wall_post_later(api, constants.groups['ru9gag'], newsitem['caption'], newsitem['link'], newsitem['path'], delay)
    elif post_type == 'wall now':
        wall_post_now(api, constants.groups['ru9gag'], newsitem['caption'], newsitem['link'], newsitem['path'])
    else:
        album_post(api, constants.groups['ru9gag'], aid, newsitem['caption'], newsitem['link'], newsitem['path'])


def get_post_type(item):
    if item.elements.directWallRB.isChecked():
        if item.elements.waitUntilCheckBox.isChecked():
            return "wall delay"
        return "wall now"
    return "album"


def upload_image(api, gid, mode, imagePath):
    link = api.call('photos.' + mode[0], group_id=gid)['upload_url']
    response = api.upload(link, imagePath, 'photo')
    return api.call('photos.' + mode[1],
                    server=response['server'],
                    photo=response['photo'],
                    hash=response['hash'],
                    group_id=gid)


def wall_post_now(api, gid, label, link, imagePath):
    image = upload_image(api, gid, ("getWallUploadServer", "saveWallPhoto"), imagePath)[0]
    attachments = ['photo' + str(image['owner_id']) + '_' + str(image['id']), link]
    api.call("wall.post", owner_id="-" + gid, from_group="1", message=label, attachments=",".join(attachments))


def wall_post_later(api, gid, label, link, imagePath, delay):
    image = upload_image(api, gid, ("getWallUploadServer", "saveWallPhoto"), imagePath)[0]
    attachments = ['photo' + str(image['owner_id']) + '_' + str(image['id']), link]
    api.call("wall.post", owner_id="-" + gid, from_group="1", message=label, attachments=",".join(attachments),
             publish_date=delay)


def album_post(api, gid, aid, label, link, imagePath):
    upload_url = api.call('photos.getUploadServer', group_id=gid, album_id=aid)['upload_url']
    response = requests.post(upload_url, files={"file1": open(imagePath, 'rb')}).json()
    image = api.call('photos.save',
                     server=response['server'],
                     photos_list=response['photos_list'],
                     hash=response['hash'],
                     group_id=gid,
                     album_id=aid,
                     caption=label)[0]
    attachments = ['photo' + str(image['owner_id']) + '_' + str(image['id']), link]
    api.call("wall.post", owner_id="-" + gid, from_group="1", message=label, attachments=",".join(attachments))


def get_album(api, gid):
    albums = api.call("photos.getAlbums", owner_id="-" + gid)['items']
    aid = None
    for album in albums:
        if album['description'].find("#9GAG_Project") != -1:
            aid = album['id']
            break
    return aid