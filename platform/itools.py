# coding: utf-8

import json
import urllib
from helper import http
from helper import utils

__VERSION__ = '2.2.0'
PLATFORM_NAME = 'itools'
APP_ID = '111'
APP_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxx'
#GAME_ID = '11097'
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC2kcrRvxURhFijDoPpqZ/IgPlA
gppkKrek6wSrua1zBiGTwHI2f+YCa5vC1JEiIi9uw4srS0OSCB6kY3bP2DGJagBo
Egj/rYAGjtYJxJrEiTxVs5/GfPuQBYmU0XAtPXFzciZy446VPJLHMPnmTALmIOR5
Dddd1Zklod9IQBMjjwIDAQAB
-----END PUBLIC KEY-----"""
GET_USER_URI = 'https://pay.slooti.com/?r=auth/verify'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'success',
    1: 'fail',
}


def login_verify(req, params=None):
    """登录验证
    Args:
        req: request封装，以下是验证所需参数
            session_id:
            nickname:
            user_id:
        params: 测试专用
    Returns:
        平台相关信息(openid必须有)
    """
    if not params:
        params = {
            'sessionid': req.get_argument('session_id', ''),
            'nickname': req.get_argument('nickname', ''),
            'user_id': req.get_argument('user_id', '')
        }
    sessionid = params['sessionid']
    nickname = params['nickname']

    sign_str = 'appid=%s&sessionid=%s' % (APP_ID, sessionid)
    sign = utils.hashlib_md5_sign(sign_str)

    query_data = urllib.urlencode({
        'appid': APP_ID,
        'sessionid': sessionid,
        'sign': sign,
    })
    url = '%s&%s' % (GET_USER_URI, query_data)
    http_code, content = http.get(url)
    #print http_code, content
    if http_code != 200:
        return None

    # {"status":"success"}
    obj = json.loads(content)
    if obj['status'] != 'success':
        return None

    openid, _ = sessionid.split('_', 1)

    return {
        'openid': openid,          # 平台id
        'openname': nickname,      # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            sign: 签名
            notify_data 解密出的结果
                {
                 u'account': u'i651866345',
                 u'amount': u'0.10',
                 u'order_id': u'2014040300303453',
                 u'order_id_com': u'h1ciw9m-h1-4-1396529027',
                 u'result': u'success',
                 u'user_id': u'563789'
                 }
        params: 测试专用
    """
    if not params:
        params = {
            'sign': req.get_argument('sign', ''),
            'notify_data': req.get_argument('notify_data', ''),
        }
    sign = params['sign']
    notify_data = params['notify_data']

    if not sign or not notify_data:
        return RETURN_DATA, None

    transdata = utils.rsa_public_decrypt(PUBLIC_KEY, notify_data, max_decrypt_block=128)
    if not utils.rsa_verify_signature(PUBLIC_KEY, transdata, sign):
        return RETURN_DATA, None

    data = json.loads(transdata)

    pay_data = {
        'app_order_id': data['order_id_com'],    # 自定义定单id
        'order_id': data['order_id'],            # 平台定单id
        'order_money': float(data['amount']),    # 平台实际支付money 单位元
        'uin': data['user_id'],                  # 平台用户id
        'platform': PLATFORM_NAME,               # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    print login_verify('', {'sessionid': '07d72e5200cb5c0031d988e618d90d5b'})




