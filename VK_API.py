import requests
import pprint
import datetime
import time
import json


def get_vk_pics(user_id, numb_photos=5, album_id='profile'):
    url_vk = 'https://api.vk.com/method/'
    params = {'access_token': 'af62a814af62a814af62a814d8af15ac2aaaf62af62a814cf3b7db0a1e3997275106265','v': "5.130"} # сервисный ключ, если что
    params_photos = {
        'owner_id': user_id,
        'album_id': album_id,
        'count': numb_photos,
        'rev': 1,
        'extended': 1
    }
    res = requests.get(url_vk + "photos.get", params={**params, **params_photos})

    # создаём список фотографий, которые нужно загрузить
    # определяем, если в списке уже есть фотография с таким же кол-вом лайков
    pic_list = {}
    log_list = []
    for picture in res.json()['response']['items']:
        if str(picture['likes']['count']) in pic_list.keys():
            date = datetime.datetime.fromtimestamp(picture['date']).strftime('%Y-%m-%d')
            item = {'{} ({})'.format(picture['likes']['count'], date): picture['sizes'][len(picture['sizes'])-1]['url']}
            pic_list.update(item)
        else:
            item = {'{}'.format(picture['likes']['count']): picture['sizes'][len(picture['sizes'])-1]['url']}
            pic_list.update(item)
        size = picture['sizes'][len(picture['sizes'])-1]['type']
        log = {"file_name": str(item.keys()), "size": size}
        log_list.append(log)

    # добавляем информацию по фотографиям в json файл
    with open('log.json', 'w') as f:
        json.dump(log_list, f, ensure_ascii=False, indent=2)
    
    return pic_list

def upload_yad(pic_list, yad_token):
    url_yad = 'https://cloud-api.yandex.net/v1/disk/'
    upload_method = 'resources/upload'
    folder_method = 'resources/'
    token = yad_token
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'OAuth ' + token}
    
    # проверяем наличие служебной папки и создаём её, если она отсутствует
    folders = requests.get(url_yad + folder_method, headers=headers, params={'path': 'disk:/', 'fields': 'name,_embedded.items.path'})
    if {'path': 'disk:/VK_pics'} not in folders.json()['_embedded']['items']:
        new_folder = requests.put(url_yad + folder_method, headers=headers, params={'path': 'disk:/VK_pics', 'fields': 'method'})
        if new_folder.status_code == 201:
            print('Папка "VK_pics" была успешно создана!')
        else:
            print('Ошибка! Папка не была создана!')

    for name, picture in pic_list.items():
        # передаём url на загрузку
        upload = requests.post(url_yad + upload_method, headers=headers, params={'url': picture, 'path': 'disk:/VK_pics/' + name + '.jpeg'})
        if upload.status_code == 202:
            # проверяем статус загрузки фотографии
            while True:
                status_req = requests.get(upload.json()['href'], headers=headers)
                status = status_req.json()["status"]
                if status == "success":
                    print(f'Готово! Фотография {name} загружена!')
                    break
                else:
                    print('Жду...')
                    time.sleep(3)
        else:
            pprint.pprint(upload.json())
    
    return "Операция закончена!"



print(upload_yad(get_vk_pics(1, 3), 'yad_token'))


