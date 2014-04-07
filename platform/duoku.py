# coding: utf-8

import json
import hashlib

PLATFORM_NAME = 'duoku'
PLATFORM_DUOKU_APP_ID = '111'
PLATFORM_DUOKU_APP_KEY = 'aaaaaaaaaaaaaaaaaaaaaaaaaaa'
PLATFORM_DUOKU_APP_SECRET = 'bbbbbbbbbbbbbbbbbbbbbbbbbbb'
PLATFORM_DUOKU_USER_URI = 'http://sdk.m.duoku.com/openapi/sdk/checksession'


def login_verify(uid, sessionid):
    """sid用户会话验证
    Args:
        uid: 平台id
        sessionid: 临时授权token
    Returns:
        token
    """
    params_data = {
        'appid': PLATFORM_DUOKU_APP_ID,
        'appkey': PLATFORM_DUOKU_APP_KEY,
        'secret': PLATFORM_DUOKU_APP_SECRET,
        'uid': uid,
        'sessionid': sessionid,
    }
    checksession = ('%(appid)s'
                    '%(appkey)s'
                    '%(uid)s'
                    '%(sessionid)s'
                    '%(secret)s'
                    ) % params_data

    new_sign = hashlib.md5(checksession).hexdigest()
    params_data['clientsecret'] = new_sign

    url = '%s?%s' % (PLATFORM_DUOKU_USER_URI, urllib.urlencode(params_data))
    http_code, content = http.get(url, timeout=30)

    if http_code != 200:
        return None

    obj = json.loads(content)
    if obj['error_code'] != 0:
        return None

    return uid


def payment_verify(params):
    """验证签名
    """
    obj = {
        'amount': params.get('amount'),
        'cardtype': params.get('cardtype'),
        'orderid': params.get('orderid'),
        'result': params.get('result'),
        'timetamp': params.get('timetamp'),
        'aid': params.get('aid'),
        'client_secret': params.get('client_secret'),
        'secret': PLATFORM_DUOKU_APP_SECRET,
    }
    result = obj['result']
    if int(result) != 1:
        return False

    pre_sign =  ('%(amount)s'
                 '%(cardtype)s'
                 '%(orderid)s'
                 '%(result)s'
                 '%(timetamp)s'
                 '%(secret)s'
                 '%(aid)s') % obj

    new_sign = hashlib.md5(pre_sign).hexdigest()

    if new_sign != obj['client_secret']:
        return False

    return params

