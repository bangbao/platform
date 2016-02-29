# coding: utf-8

import json
import hashlib
from helper import utils

# 韩文IOS平台
PLATFORM_KUNLUN_PAYMENT_KEY = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
PLATFORM_KUNLUN_SERVICE_URL = 'http://mc.sjsgkr.koramgame.com/'
PLATFORM_KUNLUN_PRODUCTID = 111
PLATFORM_KUNLUN_REGIONID = 111001
PLATFORM_KUNLUN_LOGIN_ACT = 'User.getInfo'
PLATFORM_KUNLUN_REGIST_ACT = 'User.regist'
PLATFORM_KUNLUN_INIT_ACT = 'User.init'
PLATFORM_KUNLUN_LOG_BASEPATH = r'/data/syslog/platformlog'
PLATFORM_KUNLUN_LOG_SWITCH = False
# 韩文Tstore平台
PLATFORM_KUNLUN_TSTORE_VERIFY_URL = 'http://login.koramgame.co.jp/verifyklsso.php'
# 韩文ggplay平台
PLATFORM_KUNLUN_GGPLAY_VERIFY_URL = 'http://login.koramgame.co.jp/verifyklsso.php'
PLATFORM_KUNLUN_REGIST_RETCODE = 4


def login_verify_ios(passport):
    """ 进行kor平台的信息验证
    """
    kor_passport = '%s@mac.krm' % passport
    kor_password = hashlib.md5('%s@cam' % passport).hexdigest()

    url = ("%(url)s?act=%(act)s&passport=%(passport)s&"
           "password=%(password)s") % {
                  'url': PLATFORM_KUNLUN_SERVICE_URL,
                  'act': PLATFORM_KUNLUN_LOGIN_ACT,
                  'passport': kor_passport,
                  'password': kor_password,
                }
    http_code, content = rkcurl.get(url.encode('utf-8'))
    if http_code != 200:
        return None

    obj = json.loads(content)
    kor_id = obj.get('userId')

    if not kor_id and obj['extendInfo']['result']['retcode'] == PLATFORM_KUNLUN_REGIST_RETCODE:
        url = ("%(url)s?act=%(act)s&passport=%(passport)s&"
               "password=%(password)s&repassword=%(password)s") % {
                      'url': PLATFORM_KUNLUN_SERVICE_URL,
                      'act': PLATFORM_KUNLUN_REGIST_ACT,
                      'passport': kor_passport,
                      'password': kor_password,
                    }
        http_code, content = rkcurl.get(url.encode('utf-8'), timeout=10)

        if http_code != 200:
            return None

        obj = json.loads(content)
        kor_id = obj.get('userId')

    if not kor_id:
        return None

    return passport


def login_verify_tstore(params):
    """ 进行kor Tstore平台的信息验证
    """
    openid = params.get('openid')
    openname = params.get('openname')
    kl_sso = params.get('kl_sso')

    url = ("%(url)s?klsso=%(klsso)s") % {
                  'url': PLATFORM_KUNLUN_TSTORE_VERIFY_URL,
                  'klsso': kl_sso,
                }
    http_code, content = rkcurl.get(url.encode('utf-8'))

    if http_code != 200:
        return None

    obj = json.loads(content)

    if obj['retcode'] != 0:
        return None

    kor_id = obj['data']['uid']

    if kor_id != openid:
        return None

    return openid


def login_verify_ggplay(context):
    """ 进行kor ggplay平台的信息验证
    """
    openid = params.get('openid')
    openname = params.get('openname')
    kl_sso = params.get('kl_sso')

    url = ("%(url)s?klsso=%(klsso)s") % {
                  'url': PLATFORM_KUNLUN_GGPLAY_VERIFY_URL,
                  'klsso': kl_sso,
                }
    http_code, content = rkcurl.get(url.encode('utf-8'))

    if http_code != 200:
        return None

    obj = json.loads(content)

    if obj['retcode'] != 0:
        return None

    kor_id = obj['data']['uid']

    if kor_id != openid:
        return None

    return openid


def payment_verify(params):
    """ kor 回调接口
    """
    obj = {
        'oid': params.get('oid'),
        'kor_id': params.get('uid'),
        'amount': params.get('amount'),
        'coins': params.get('coins'),
        'dtime': params.get('dtime'),
        'sign': params.get('sign'),
        'ext': params.get('ext'),
        'KEY': PLATFORM_KUNLUN_PAYMENT_KEY,
    }

    pre_sign = ("%(oid)s"
                "%(kor_id)s"
                "%(amount)s"
                "%(coins)s"
                "%(dtime)s"
                "%(KEY)s") % obj
    new_sign = hashlib.md5(pre_sign).hexdigest()

    if new_sign != obj['sign']:
        return False

    return obj

