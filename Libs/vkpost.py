__author__ = 'Alexander'

import os, requests


def upload_image(api, gid, mode, imagePath):
    link = api.call('photos.' + mode[0], group_id=gid)['upload_url']
    os.rename(imagePath, imagePath + '.jpg')
    imagePath += '.jpg'
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
    os.rename(imagePath, imagePath + '.jpg')
    imagePath += '.jpg'
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