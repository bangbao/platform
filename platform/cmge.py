# encoding: utf-8

import json
import urllib
from helper import http
from helper import utils

__VERSION__ = 'v1.1'
PLATFORM_NAME = 'cmge'  # 中手游ios正版
PRODUCT_ID = 'xxxxx'
SERVER_ID = 'xxxxx'
PROJECT_ID = 'xxxxxxx'
SYN_KEY = 'xxxxxxxxxxxxxxxxxxxx'
APP_KEY = 'xxxxxxxxxxxxxxxxxx'
APP_SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxx'
APP_USERINFO_URL = 'http://yx.sdksrv.com/sdksrv/auth/getUserInfo.lg'


def login_verify(req, params=None):
    """登录验证
    Args:
        req: request封装，以下是验证所需参数
            session_id: session_id
        params: 测试专用
    Returns:
        平台相关信息(openid必须有)
    """
    if not params:
        params = {
            'session_id': req.get_argument('session_id', ''),
            'user_id': req.get_argument('user_id', ''),
        }
    access_token = params['session_id']
    user_id = params['user_id']

    post_data = {
        'access_token': access_token,
        'productId': PRODUCT_ID,
        '__e__': '1',
    }

    params_keys = sorted(((k, v) for k, v in post_data.iteritems() if v))
    sign_values = ('%s=%s' % (k, v) for k, v in params_keys)
    sign_data1 = '&'.join(sign_values)
    sign_data = '%s&%s' % (sign_data1, APP_KEY)
    sign0 = utils.hashlib_md5_sign(sign_data)
    sign1 = list(sign0)
    trans_template = [(1, 13), (5, 17), (7, 23)]
    for start, end in trans_template:
        sign1[start], sign1[end] = sign1[end], sign1[start]
    sign = ''.join(sign1)
    post_data['sign'] = sign

    query_data = urllib.urlencode(post_data)

    http_code, content = http.post(APP_USERINFO_URL, query_data)
    # print http_code, content
    if http_code != 200:
        return None

    # {"codes":"1"}
    # 0成功, 1失败
    obj = json.loads(content)
    # print obj['codes']
    if int(obj['codes']) != 0:
        return None

    return {
        'openid': obj['sdkuserid'],    # 平台标识
        'openname': obj['username'],   # 平台昵称
    }

if __name__ == '__main__':
    params = {'session_id': 'edbee930-91a', 'user_id': 'U24062'}
    print login_verify('', params)


