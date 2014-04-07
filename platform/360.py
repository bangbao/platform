# coding: utf-8

import utils
import json
import hashlib

PLATFORM_NAME = '360'
PLATFORM_360_APP_ID = '11111111'
PLATFORM_360_APP_KEY = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
PLATFORM_360_APP_SECRET = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
PLATFORM_360_USER_URI = 'https://openapi.360.cn/user/me.json'
PLATFORM_360_VERIFY_URI = 'https://openapi.360.cn/pay/verify_mobile_notification.json'
PLATFORM_360_ACCESS_TOKEN_URI = 'https://openapi.360.cn/oauth2/access_token'


def login_verify(access_token=None, authorization_code=None):
    """sid用户会话验证
    Args:
        access_token: 从游戏客户端的请求中获取的access_token值
        authorization_code: authorization_code
    Returns:
        用户标识
    """
    if access_token is None:
        access_token = get_access_token(authorization_code)

    url = '%(url)s?access_token=%(access_token)s' % {
                'url': PLATFORM_360_USER_URI,
                'access_token': access_token}

    http_code, content = utils.http.get(url, timeout=30)

    if http_code != 200:
        return None

    obj = json.loads(content)

    return obj['id']


def payment_verify(params):
    """支付回调验证，app_order_id为自定义
    Args:
        params: 字典参数数据
    Returns:
        支付数据
    """
    if params['gateway_flag'] != "success":
        return False

    params['client_id'] = PLATFORM_360_APP_KEY
    params['client_secret'] = PLATFORM_360_APP_SECRET

    url = '%s?%s' % (PLATFORM_360_VERIFY_URI, urllib.urlencode(params))
    http_code, content = utils.http.get(url, timeout=30)

    if http_code != 200:
        return False

    obj = json.loads(content)

    if obj['ret'] != 'verified':
        return False

    # 按key自然排序
    sign_keys = ('amount', 'app_ext1', 'app_ext2', 'app_order_id', 'app_uid',
                 'gateway_flag', 'order_id', 'product_id', 'sign_type', 'user_id')
    sign_values = [params[key] for key in sign_keys]
    sign_values.append(PLATFORM_360_APP_SECRET)
    sign_str = '#'.join(sign_values)
    new_sign = hashlib.md5(sign_str).hexdigest()

    if new_sign != params['sign']:
        return False

    return obj


def get_access_token(self, authorization_code):
    """通过code获得token
    Args:
        authorization_code: authorization_code
    """
    url = ('%(url)s?code=%(code)s&grant_type=authorization_code&redirect_uri=oob&'
           'client_id=%(client_id)s&client_secret=%(client_secret)s') % {
                'url': PLATFORM_360_ACCESS_TOKEN_URI,
                'client_id': PLATFORM_360_APP_KEY,
                'client_secret': PLATFORM_360_APP_SECRET,
        }

    http_code, content = utils.http.get(url, timeout=30)

    if http_code != 200:
        return None

    obj = json.loads(content)

    return obj['access_token']


