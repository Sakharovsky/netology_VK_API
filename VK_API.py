import requests
import pprint

class VkUser:
    url = 'https://api.vk.com/method/'
    version = '5.130'

    def __init__(self, token):
        self.token = token
        self.params = {
            'access_token': self.token,
            'v': self.version     
        }
        self.owner_id = requests.get(self.url+'users.get', self.params).json()['response'][0]['id']
    
    
    def get_followers(self, user_id=None):
        if user_id is None:
            user_id = self.owner_id
        followers_url = self.url + 'users.getFollowers'
        followers_params = {
            'count': 1000,
            'user_id': user_id
        }
        res = requests.get(followers_url, params={**self.params, **followers_params})
        return res.json()

admin = VkUser('')

pprint.pprint(admin.get_followers())

