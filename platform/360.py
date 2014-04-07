# coding: utf-8

import utils
import json
import hashlib

SDK_360_APP_ID = '11111111'
SDK_360_APP_KEY = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
SDK_360_APP_SECRET = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
SDK_360_USER_URI = 'https://openapi.360.cn/user/me.json'
SDK_360_VERIFY_URI = 'https://openapi.360.cn/pay/verify_mobile_notification.json'
SDK_360_ACCESS_TOKEN_URI = 'https://openapi.360.cn/oauth2/access_token'


def login_verify(access_token=None, authorization_code=None):
    """sid用户会话验证
    Args:
        access_token: 从游戏客户端的请求中获取的access_token值
    """
    if access_token is None:
        access_token = get_access_token(authorization_code)

    url = '%(url)s?access_token=%(access_token)s' % {
              'url': SDK_360_USER_URI,
              'access_token': access_token,
          }

    http_code, content = utils.http.get(url, timeout=30)

    if http_code != 200:
        return None

    obj = json.loads(content)

    openid = obj.get('id', None)

    if not openid:
        return None

    return openid


def payment_verify(params):
    """
    app_order_id
    """
    gateway_flag = params.get('gateway_flag')
    if gateway_flag != "success":
        return None

    params['client_id'] = SDK_360_APP_KEY
    params['client_secret'] = SDK_360_APP_SECRET

    url = '%s?%s' % (SDK_360_VERIFY_URI, urllib.urlencode(params))
    http_code, content = utils.http.get(url, timeout=30)

    if http_code != 200:
        return False

    obj = json.loads(content)

    status = obj.get('ret', 'invalid')

    if status != 'verified':
        return False

    exclude_sign_params = ['sign', 'method', 'type', 'server_id',
                           'sign_return', 'client_id', 'client_secret']

    data = [(k, v) for k, v in params.iteritems() if v and k not in exclude_sign_params]
    data.sort(key=lambda x : x[0])
    sign_str = '%s#%s' % ('#'.join(data.itervalues()), SDK_360_APP_SECRET)
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
                'url': SDK_360_ACCESS_TOKEN_URI,
                'client_id': SDK_360_APP_KEY,
                'client_secret': SDK_360_APP_SECRET,
        }

    http_code, content = utils.http.get(url, timeout=30)

    if http_code != 200:
        return None

    obj = json.loads(content)

    return obj.get('access_token')


