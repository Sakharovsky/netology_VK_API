import requests
import pprint


def get_vk_pics(user_id=None, album_id='profile', numb_photos=5):
    url_vk = 'https://api.vk.com/method/'
    params = {
        'access_token': '',
        'v': "5.130"
    }
    owner_id = requests.get(url_vk + 'users.get', params).json()['response'][0]['id']

    if user_id == None:
        user_id = owner_id
    
    params_photos = {
        'owner_id': user_id,
        'album_id': album_id,
        'count': numb_photos,
        'rev': 1,
        'extended': 1
    }

    res = requests.get(url_vk + "photos.get", params={**params, **params_photos})

    # создаём список последних фотографий
    # определяем, если в списке уже есть фотография с таким же кол-вом лайков
    pic_list = {}
    for picture in res.json()['response']['items']:
        if str(picture['likes']['count']) in pic_list.keys(): 
            pic_list.update({'{} ({})'.format(picture['likes']['count'], picture['date']): picture['sizes'][len(picture['sizes'])-1]['url']})
        else:
            pic_list.update({'{}'.format(picture['likes']['count']): picture['sizes'][len(picture['sizes'])-1]['url']})
    
    return pic_list

pprint.pprint(get_vk_pics())

