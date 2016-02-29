# coding: utf-8

import utils
import json
import hashlib

PLATFORM_NAME = 'sina_dating'
PLATFORM_SINA_DATING_APP_KEY = '111111111'
PLATFORM_SINA_DATING_APP_SECRET = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
PLATFORM_SINA_DATING_USER_URL = 'https://api.weibo.com/2/users/show.json'
PLATFORM_SINA_DATING_VERIFY_URL = 'http://i.game.weibo.cn/pay.php'

PLATFORM_SINA_WEIBO_USER_URL = 'https://api.weibo.com/2/users/show.json'
PLATFORM_SINA_WEIBO_APP_KEY = '11111111'
PLATFORM_SINA_WEIBO_APP_SECRET = 'aaaaaaaaaaaaaaaaaaaaaaaa'


def login_verify(uid, access_token):
    """
    """
    url = ('%(url)s?access_token=%(access_token)s&uid=%(uid)s&'
           'source=%(source)s') % {
                    'url': PLATFORM_SINA_DATING_USER_URL,
                    'source': PLATFORM_SINA_DATING_APP_KEY,
                    'access_token': access_token,
                    'uid': uid}

    http_code, content = utils.http.get(url, timeout=30)

    if http_code != 200:
        return None

    obj = json.loads(content)
    if obj['error_code'] != 0:
        return None

    return obj['id']


def payment_verify(body, sessionkey):
    """
    sessionkey: 用户登陆时保存的key
    """
    status = params.get('status')

    if status and status == "F":
        return None

    params = {
        'order_id': body.get('order_id'),
        'amount': body.get('amount'),
        'order_uid': body.get('order_uid'),
        'source': body.get('source'),
        'actual_amount': body.get('actual_amount'),
    }
    signature = body.get('signature')

    url = ('%(url)s?method=%(method)s&order_id=%(order_id)s&'
           'sessionkey=%(sessionkey)s') % {
                    'url': PLATFORM_SINA_DATING_VERIFY_URL,
                    'method': 'query',
                    'order_id': params['order_id'],
                    'sessionkey': sessionkey,
                    }

    http_code, content = utils.http.get(url, timeout=30)

    if http_code != 200:
        return False

    obj = json.loads(content)
    if obj['error_code'] != 0:
        return False

    if obj['order_status'] != 2:
        return False

    exclude_sign_params = ['signature', 'method', 'type', 'server_id']
    data = [(k, v,) for k, v in params.iteritems() if v and k not in exclude_sign_params]
    data.sort(key=lambda x: x[0])
    list_data = ['%s|%s' % (k, v) for k, v in data]
    sign_str = '%s|%s' % ('|'.join(list_data), PLATFORM_SINA_DATING_APP_SECRET)

    sign = hashlib.sha1(sign_str).hexdigest()
    if sign != signature:
        return False

    return obj

