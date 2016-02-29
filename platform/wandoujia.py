# coding: utf-8

import json
import urllib
from helper import http
from helper import utils

__VERSION__ = '3.2.6'
PLATFORM_NAME = 'wandoujia'
APP_KEY = '11111'
APP_SECRET = "xxxxxxxxxxxxxxxxxxxxx"
# APP_KEY = '100025117'
# APP_SECRET = "15d1503aaea9b2ffa4b1b51616a09598"
APP_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCd95FnJFhPinpNiE/h4VA6bU1r
zRa5+a25BxsnFX8TzquWxqDCoe4xG6QKXMXuKvV57tTRpzRo2jeto40eHKClzEgj
x9lTYVb2RFHHFWio/YGTfnqIPTVpi7d7uHY+0FZ0lYL5LlW4E2+CQMxFOPRwfqGz
Mjs1SDlH7lVrLEVy6QIDAQAB
-----END PUBLIC KEY-----"""
VERIFY_USER_URL = "https://pay.wandoujia.com/api/uid/check"
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'success',
    1: 'fail',
}


def login_verify(req, params=None):
    """登录验证
    Args:
        uid: 平台ID
        token: 会话token
    """
    if not params:
        params = {
            'session_id': req.get_argument('session_id', ''),
            'user_id': req.get_argument('user_id', ''),
        }
    uid = params['user_id']
    token = params['session_id']

    query_data = urllib.urlencode({
        'uid': uid,
        'token': token,
        'appkey_id': APP_KEY,
    })
    url = '%s?%s' % (VERIFY_USER_URL, query_data)
    http_code, content = http.get(url)
    # print http_code, content
    if http_code != 200:
        return None

    if content != 'true':
        return None

    return {
        'openid': uid,          # 平台标识
        'openname': uid,        # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        params: 字典参数数据
            sign: 签名
            signType: 签名类型 值固定 RSA
            content: 支付json格式数据
                timeStamp    时间戳
                orderId      豌豆荚订单id
                money        支付金额 单位是（分）
                chargeType   支付类型
                appKeyId     appKeyId
                buyerId      购买人的账户id
                out_trade_no 开发者订单号  创建订单时候传入的订单号原样返回
                cardNo       充值卡id     只有充值卡充值的时候才不为空
    """
    if not params:
        params = {
            'sign': req.get_argument('sign', ''),
            'signType': req.get_argument('signType', ''),
            'content': req.get_argument('content', ''),
        }
    sign = params['sign']
    content = params['content'].encode('utf-8')

    if not utils.rsa_verify_signature(APP_PUBLIC_KEY, content, sign):
        return RETURN_DATA, None

    obj = json.loads(content)
    pay_data = {
        'app_order_id': obj['out_trade_no'],         # 自定义定单id
        'order_id': obj['orderId'],                  # 平台定单id
        'order_money': float(obj['money']) / 100,    # 平台实际支付money 单位元
        'uin': obj['buyerId'],                       # 平台用户id
        'platform': PLATFORM_NAME,                   # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    # print login_verify('', {'session_id': '11111', 'user_id': 'bbbbbb'})
    sign = 'RJmiQvnn8x4mtXHJ3+x6Mgn2HQig/0T45UYtMjBI9Kw17s3rbPfwJSwBRKLXmGfH+NWHc2YDKfuToOEWS6u3QsEiHTTg5ACS317dd234XSQjHlBwypPT06w2iKwwAPyvfljFUFLKoZ2szsVgrJ509QWj2SRC4ZzsnSjSPXIWQiE='
    content = '{"orderId":116994119,"appKeyId":100001457,"buyerId":51906841,"cardNo":null,"money":100,"chargeType":"ALIPAY","timeStamp":1397652720897,"out_trade_no":"h10032893-h1-1-1397652691"}'
    print payment_verify('', {'sign': sign, 'content': content})


