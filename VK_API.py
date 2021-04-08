import requests
import pprint
import datetime
import time
import json


def get_vk_pics(access_token, user_id=None, numb_photos=5, album_id='profile'):
    """Возвращает список словарей с лайками, датой, параметрами размера и ссылкой на скачивание.
    Возвращает False, если произошла ошибка."""
    
    url_vk = 'https://api.vk.com/method/'
    params = {'access_token': access_token, 'v': "5.130"}
    if user_id is None:
        user_id = requests.get(url_vk + 'users.get', params=params).json()['response'][0]['id']
    params.update({'owner_id': user_id, 'album_id': album_id, 'count': numb_photos, 'rev': 1, 'extended': 1})

    res = requests.get(url_vk + 'photos.get', params=params)

    if res.status_code == 200 and 'error' not in res.json():
        pic_list = []
        for picture in res.json()['response']['items']:
            date = datetime.datetime.fromtimestamp(picture['date']).strftime('%Y-%m-%d')
            likes = picture['likes']['count']
            size_type = picture['sizes'][len(picture['sizes'])-1]['type']
            size_height = picture['sizes'][len(picture['sizes'])-1]['height']
            size_width = picture['sizes'][len(picture['sizes'])-1]['width']
            url = picture['sizes'][len(picture['sizes'])-1]['url']
            pic_list.append({'Likes': likes, 'Date': date, 'Size type': size_type,
                             'Size height': size_height, 'Size width': size_width, 'Url': url})
        return pic_list
    else:
        return False


def folder_yad(yad_token, folder='VK_pics'):
    """Функция создаёт папку на Яндекс Диске, если папка с таким названием не существует.
    Возвращает True, если папка была или была создана. При ошибке False."""

    url_yad = 'https://cloud-api.yandex.net/v1/disk/resources/'
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'OAuth ' + yad_token}
    folders = requests.get(url_yad, headers=headers, params={'path': 'disk:/', 'fields': 'name,_embedded.items.path'})

    if {'path': 'disk:/' + folder} not in folders.json()['_embedded']['items']:
        new_folder = requests.put(url_yad, headers=headers, params={'path': 'disk:/' + folder, 'fields': 'method'})
        if new_folder.status_code == 201:
            print(f'Папка "{folder}" была успешно создана!')
            return True
        else:
            print('Ошибка! Папка не была создана!')
            return False
    else:
        print(f'Папка "{folder}" уже существует на диске!')
        return True


def upload_yad(pic_list, yad_token, folder):
    """Функция загружает фотографии на Яндекс Диск. В качестве имени берётся кол-во лайков. Если они дублируются,
    дополнительно присваивается дата создания.
    Возвращает список загруженных фотографий в виде словарей."""

    url_yad = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'OAuth ' + yad_token}
    name_list = []
    upload_pics = []

    for picture in pic_list:
        # выбираем имя
        if str(picture['Likes']) in name_list:
            name = str(picture['Likes']) + f" ({picture['Date']})"
        else:
            name = str(picture['Likes'])
        name_list.append(name)

        upload = requests.post(url_yad, headers=headers, params={'url': picture['Url'],
                                                                 'path': 'disk:/' + folder + '/' + name + '.jpeg'})

        # проверяем статус загрузки фотографии
        if upload.status_code == 202:
            while True:
                status_req = requests.get(upload.json()['href'], headers=headers)
                status = status_req.json()["status"]
                if status == "success":
                    print(f'Готово! Фотография {name} загружена!')
                    picture.update({'Name': name})
                    upload_pics.append(picture)
                    break
                else:
                    print('Жду...')
                    time.sleep(3)
        else:
            pprint.pprint(upload.json())
    
    return upload_pics


def log_pics(pic_list):
    """Функция создаёт json файл с информацией по сохранённым фотографиям.
    Возвращает True или False."""
    log = []
    for picture in pic_list:
        log.append({'file_name': picture['Name'], 'size': picture['Size type']})

    with open('log.json', 'w') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


vk_token = input('Введите токен ВК: ')
yad_token = input('Введите токен Яндекс Диск: ')

vk_user = input('''Введите номер ID пользователя ВК 
(оставьте пустым для выбора владельца токена): ''')
if vk_user == '':
    vk_user = None
else:
    vk_user = int(vk_user)

vk_album = input('''Введите название папки, откуда сохранять фотограции 
(оставьте пустым для выбора папки с фотографиями профиля): ''')
if vk_album == '':
    vk_album = 'profile'

numb_pics = input('''Введите количество последних фотографий для сохранения
(оставьте пустым для сохранения 5 последних фотографий): ''')
if numb_pics == '':
    numb_pics = 5
else:
    numb_pics = int(numb_pics)

folder = input('''Введите название папки на Яндекс Диск
(оставьте пустым для загрузки в папку VK_pics): ''')
if folder == '':
    folder = 'VK_pics'

folder_yad(yad_token, folder=folder)
vk_list = get_vk_pics(vk_token, user_id=vk_user, numb_photos=int(numb_pics), album_id=vk_album)
yad_list = upload_yad(vk_list, yad_token, folder)
log_pics(yad_list)


