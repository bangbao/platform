# coding: utf-8

import utils
import json
import hashlib
import hmac

PLATFORM_NAME = 'xiaomi'
PLATFORM_XIAOMI_APP_ID = '11111'
PLATFORM_XIAOMI_APP_KEY = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
PLATFORM_XIAOMI_APP_URL = "http://mis.migc.xiaomi.com/api"
PLATFORM_XIAOMI_VERIFY_SESSION_URL = 'http://mis.migc.xiaomi.com/api/biz/service/verifySession.do'

## xiaomi platform return code:
RETURN_CODE = {
    'SUCESS': 200,
    'E_CPORDERID': 1506,
    'E_APPID': 1515,
    'E_UID': 1516,
    'E_SIGN': 1525,
    'E_UNIFORM': 3515,
    'E_UNKOWN': 3510
}


def login_verify(uid, session_id):
    """
    """
    params = {
        'appId':PLATFORM_XIAOMI_APP_ID,
        'uid':uid,
        'session':session_id,
    }
    signature = xiaomi_make_sign(params)
    url = ('%(url)s?appId=%(appId)s&session=%(session)s&uid=%(uid)s&'
           'signature=%(signature)s') % {
                'url': PLATFORM_XIAOMI_VERIFY_SESSION_URL,
                'appId': APP_ID,
                'session': session_id,
                'uid': uid,
                'signature': signature}

    http_code, content = utils.http.get(url, timeout=10)

    if http_code != 200:
        return None

    result = json.loads(content)
    if result['errcode'] != 200:
        return None

    return result['uid']


def payment_verify(params):
    """验证支付
    @params(context.params):
        'orderId': 游戏平台订单id
        'payFee': 米币
        'productName': 商品名称
        'ProductCount': 商品数量
        'payTime': 支付时间
        'cpOrderId': 开发商订单id
        'uid': 玩家id
    """
    result_data = {
        'status': 0,
        'skip': False
    }

    uid = params.get('uid')
    if not uid:
        result_data['status'] = RETURN_CODE['E_UID']
        return result_data

    if params['orderStatus'] != 'TRADE_SUCCESS':
        result_data['status'] = RETURN_CODE['E_UNKOWN']
        return result_data

    if params['appId'] != APP_ID:
        result_data['status'] = RETURN_CODE['E_APPID']
        return result_data

    sign = xiaomi_make_sign(params)
    if sign != params['signature']:
        result_data['status'] = RETURN_CODE['E_SIGN']
        return result_data

    return result_data


def xiaomi_make_sign(params):
    """制作签名 按字母顺序排序 使用hmac-sha1"""
    keys = params.keys()
    keys.sort()
    values = []
    for k in keys:
        if k not in ['signature', 'method', 'type', 'server_id']:
            values.append("%s=%s" % (k, params[k]))
    msg = '&'.join(values)
    signature = hmac.new(PLATFORM_XIAOMI_APP_KEY, msg, hashlib.sha1).hexdigest()
    return signature


