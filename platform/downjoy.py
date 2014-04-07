# encoding: utf-8

import json
import hashlib

#登陆当乐的请求url
PLATFORM_DOWNLOY_APP_URL = 'http://connect.d.cn/open/member/info/'
#接入时由当乐分配的游戏/应用ID。
PLATFORM_DOWNLOY_APP_ID = "111"
#接入时由当乐分配的游戏/应用密钥。
PLATFORM_DOWNLOY_APP_KEY = "aaaaaaaa"
#支付模块
PLATFORM_DOWNLOY_PAYMENT_KEY = "bbbbbbbb"


def login_verify(mid, token):
    """获取当前登录用户信息
    Args:
        mid: 平台id
        token: 临时授权token
    """
    sig = hashlib.md5(token + "|" + PLATFORM_DOWNLOY_APP_KEY).hexdigest()
    
    url = '%(url)s?app_id=%(app_id)s&mid=%(mid)s&token=%(token)s&sig=%(sig)s' % {
                'app_id': PLATFORM_DOWNLOY_APP_ID,
                'mid': mid,
                'token': token,
                'sig': sig,
                'url': PLATFORM_DOWNLOY_APP_URL}

    http_code, content = utils.http.get(url, timeout=30)

    if http_code != 200:
        return None

    obj = json.loads(content)
    if obj['error_code'] != 0:
        return None

    return mid


def payment_verify(params):
    """验证签名
    """
    params['key'] = PLATFORM_DOWNLOY_APP_KEY

    pre_sign = ('%(order)s'
                '%(money)s'
                '%(mid)s'
                '%(time)s'
                '%(result)s'
                '%(ext)s'
                '%(key)s') % params

    new_sign = hashlib.md5(pre_sign).hexdigest()

    if new_sign != params.get("signature"):
        return False

    return params



