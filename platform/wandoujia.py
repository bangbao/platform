# coding: utf-8

import utils
import urllib

PLATFORM_NAME = 'wandoujia'
PLATFORM_WANDOUJIA_APP_ID = '111111111'
PLATFORM_WANDOUJIA_APP_SECRET = "aaaaaaaaaaaaaaaaaaaaaaaaaa"
PLATFORM_WANDOUJIA_APP_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
......................
-----END PUBLIC KEY-----"""
PLATFORM_WANDOUJIA_USER_URL = "https://pay.wandoujia.com/api/uid/check"


def login_verify(uid, token):
    """登录验证
    """
    url = '%(url)s?%uid=%(uid)s&token=%(token)s' % {
                'url': PLATFORM_WANDOUJIA_USER_URL,
                'uid': uid,
                'token': token,
            }

    status, content = utils.http.get(url, timeout=5)
    if status != 200:
        return False

    if content != 'true':
        return False

    return uid


def payment_verify(params):
    """支付回调验证
    """
    sign = params.get('sign')
    content = params.get('content')

    if not utils.rsa_verify_signature2(PLATFORM_WANDOUJIA_APP_PUBLIC_KEY, content, sign):
        return False

    return json.loads(content)



