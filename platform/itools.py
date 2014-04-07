# coding: utf-8

#     params example:
#     {
#      u'account': u'i651866345',
#      u'amount': u'0.10',
#      u'order_id': u'2014040300303453',
#      u'order_id_com': u'aaaaaa-h1-4-1396529027',
#      u'result': u'success',
#      u'user_id': u'563789'
#      }

import utils
import json

PLATFORM_NAME = 'itools'
PLATFORM_ITOOLS_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
......
-----END PUBLIC KEY-----"""


def login_verify(token):
    return token


def payment_verify(params):
    """支付验证
    order_id_com
    """
    sign = params.get('sign', '')
    notify_data = params.get('notify_data', '')

    content_list = []
    begin = 0
    b64string = base64.decodestring(notify_data)
    for length in xrange(128, len(b64string), 128):
        sign_data = b64string[begin:length]
        _data = utils.rsa_public_decrypt(PLATFORM_ITOOLS_PUBLIC_KEY, sign_data)
        content_list.append(_data)
        begin = length

    content = ''.join(content_list)
    result = json.loads(content)

    return result

