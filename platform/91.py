# coding: utf-8

import json

IS_IOS = True

if IS_IOS:
    PLATFORM_NAME = 'ios91'
    PLATFORM_91_APP_ID = 000001
    PLATFORM_91_APP_KEY = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
else:
    PLATFORM_NAME = 'android91'
    PLATFORM_91_APP_ID = 000002
    PLATFORM_91_APP_KEY = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'

PLATFORM_91_LOGIN_ACT_ID = 4
PLATFORM_91_PAY_ACT_ID = 1
PLATFORM_91_APP_URL = 'http://service.sj.91.com/usercenter/AP.aspx'


def login_verify(uin, sid):
    """
    Args:
        uin: 用户的91Uin
        sid: 用户登录91SessionId
    Returns:
        user_token
    """
    sign_str = "%d%d%s%s%s" % (PLATFORM_91_APP_ID, PLATFORM_91_LOGIN_ACT_ID,
                               uin, sid, PLATFORM_91_APP_KEY)
    sign = hashlib.md5(sign_str).hexdigest()

    url = ("%(url)s?AppId=%(app_id)d&Act=%(act)d&Uin=%(uin)s&"
              "Sign=%(sign)s&SessionID=%(sid)s") % {
                  'url': PLATFORM_91_APP_URL,
                  'app_id': PLATFORM_91_APP_ID,
                  'act': PLATFORM_91_LOGIN_ACT_ID,
                  'uin': uin,
                  'sid': sid,
                  'sign': sign,
                }

    http_code, content = utils.http.get(url)

    if http_code != 200:
        return None

    obj = json.loads(content)

    if obj['ErrorCode'] != 0:
        return None

    return uin


def payment_verify(params):
    """params 为91服务器回调的参数们
    """
    obj = {
        'app_id': PLATFORM_91_APP_ID,
        'act': PLATFORM_91_PAY_ACT_ID,
        'app_key': PLATFORM_91_APP_KEY,
        'product_name': params.get('ProductName', '').encode('utf-8'),
        'consume_stream_id': params.get('ConsumeStreamId', ''),
        'coo_order_serial': params.get('CooOrderSerial', ''),
        'uin': params.get('Uin', ''),
        'goods_id': params.get('GoodsId', ''),
        'goods_info': params.get('GoodsInfo', '').encode('utf-8'),
        'goods_count': int(params.get('GoodsCount', 0)),
        'original_money': float(params.get('OriginalMoney', 0)),
        'order_money': float(params.get('OrderMoney', 0)),
        'note': params.get('Note', '').encode('utf-8'),
        'pay_status': int(params.get('PayStatus', 0)),
        'create_at': params.get('CreateTime', ''),
        'sign': params.get('Sign', ''),
    }

    if not obj['pay_status']:
        return False

    pre_sign = ("%(app_id)d"
                "%(act)d"
                "%(product_name)s"
                "%(consume_stream_id)s"
                "%(coo_order_serial)s"
                "%(uin)s"
                "%(goods_id)s"
                "%(goods_info)s"
                "%(goods_count)d"
                "%(original_money).2f"
                "%(order_money).2f"
                "%(note)s"
                "%(pay_status)d"
                "%(create_at)s"
                "%(app_key)s") % obj

    new_sign = hashlib.md5(pre_sign).hexdigest()
    if new_sign != sign:
        return False

    return obj



