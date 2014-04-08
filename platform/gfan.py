# coding: utf-8

import utils
import json
import hashlib
import urllib

PLATFORM_NAME = 'gfan'
PLATFORM_GFAN_APP_UID = 111111
PLATFORM_GFAN_APP_ID = 11111111
PLATFORM_GFAN_APP_KEY = 'aaaaaaaa'
PLATFORM_GFAN_VERIFY_URL = 'http://api.gfan.com/uc1/common/verify_token'


def login_verify(token):
    """登录验证
    """
    post_data = {'token': token}
    user_agent = 'packageName=%s,appName=%s,channelID=%s' % ('pack_name', 'app_name', PLATFORM_GFAN_APP_KEY)
    http_code, content = utils.http.post(PLATFORM_GFAN_VERIFY_URL,
                                         urllib.urlencode(post_data),
                                         headers={'User-Agent': user_agent})

    if http_code != 200:
        return None

    obj = json.loads(content)

    if obj['resultCode'] != 1:
        return None

    return obj['uid']


def payment_verify(params, post_data):
    """order_id
    post_data: 回调的原始数据
    """
    dict_data = utils.xml2dict(post_data)
    obj = {
        'sign': params.get('sign'),
        'time': params.get('time'),
        'cost': dict_data.get('cost'),
        'appkey': dict_data.get('appkey'),
        'create_time': dict_data.get('create_time'),
        'order_id': dict_data.get('order_id'),
    }

    pre_sign = "%s%s" % (APP_UID, obj['time'])
    new_sign = hashlib.md5(pre_sign).hexdigest()
    if new_sign != obj['sign']:
        return False

    return obj


