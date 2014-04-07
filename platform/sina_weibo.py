# coding: utf-8

import utils
import json

PLATFORM_SINA_WEIBO_USER_URL = 'https://api.weibo.com/2/users/show.json'
PLATFORM_SINA_WEIBO_APP_KEY = '111111111'
PLATFORM_SINA_WEIBO_APP_SECRET = 'aaaaaaaaaaaaaaaaaaaaaaaaaaa'


def login_verify(uid, access_token):
    """
    uid: 微波数字ID
    access_token: 授权的token
    """
    url = '%(url)s?access_token=%(access_token)s&uid=%(uid)s' % {
                'url': PLATFORM_SINA_WEIBO_USER_URL,
                'access_token': access_token,
                'uid': uid}

    http_code, content = utils.http.get(url, timeout=30)

    if http_code != 200:
        return None

    obj = json.loads(content)
    if obj['error_code'] != 0:
        return None

    return obj['id']

