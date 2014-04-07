# coding: utf-8

import base64
import hashlib

PLATFORM_NAME = 'ANZHI'
PLATFORM_ANZHI_PAYMENT_SECRET_KEY = 'aaaaaaaaaaaaaaaaaaaaaaaaa'


def login_verify(openid):
    """登陆验证
    Args:
        openid: 平台id
    Returns:
        token
    """
    return '%s_%s' % (PLATFORM_NAME, openid)


def payment_verify(params):
    """支付验证
    "amount=30.0&signStr=sE1BC7F4B76FCCC934439915EB40A6432&payResult=200&payType=001&msg=SUCCESS&ext=bbbbbbbbbbbbbbbbbbbbbbb&orderId=20130910-137858-0808421160004198&appKey=sk7Ep9zpp7yNI3Q8YK8mv3Cw"
    Args:
        params: 回调字典数据
    """
    obj = {
        'appKey': params.get('appKey'),
        'amount': params.get('amount'),
        'orderId': params.get('orderId'),
        'payResult': params.get('payResult', 0),
        'signStr': params.get('signStr'),
        'msg': params.get('msg', ''),
        'ext': params.get('ext'),
        'payType': params.get('payType'),
        'KEY': PLATFORM_ANZHI_PAYMENT_SECRET_KEY,
    }

    if int(obj['payResult']) != 200:
        return False

    pre_sign = ("%(appKey)s"
                "%(amount)s"
                "%(orderId)s"
                "%(payResult)s"
                "%(ext)s"
                "%(msg)s"
                "%(KEY)s") % obj

    new_sign = hashlib.md5(pre_sign).hexdigest()
    if new_sign.upper() != obj['signStr']:
        return False

    #b64decode_str = base64.b64decode(obj['ext'])
    #billno_list = b64decode_str.split('_')
    #user_id, create_at, add_kcoin, scheme_id, first_double = billno_list

    return obj

