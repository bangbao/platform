# coding: utf-8

import json
from helper import oauth
from helper import http
from helper import utils

__VERSION__ = '1.6.7'
PLATFORM_NAME = 'oppo'
APP_ID = '1111'
APP_KEY = 'xxxxxxxxxxxxxxxxxx'
APP_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
APP_RSA_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCmreYIkPwVovKR8rLHWlFVw7YD
fm9uQOJKL89Smt6ypXGVdrAKKl0wNYc3/jecAoPi2ylChfa2iRu5gunJyNmpWZzl
CNRIau55fxGW0XEu553IiprOZcaw5OuYGlf60ga8QT6qToP0/dpiL/ZbmNUO9kUh
osIjEu22uFgR+5cYyQIDAQAB
-----END PUBLIC KEY-----"""
GET_USERINFO_URI = 'http://thapi.nearme.com.cn/account/GetUserInfoByGame'
REQUEST_METHOD = 'GET'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'result=OK&resultMsg=SUCCESS',
    1: 'result=FAIL&resultMsg=signerror',
}


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
            'nickname': req.get_argument('nickname', ''),
        }
    oauth_token = params['session_id']
    oauth_token_secret = params['nickname']

    consumer = oauth.OAuthConsumer(APP_KEY, APP_SECRET)
    token = oauth.OAuthToken(oauth_token.encode('utf-8'), oauth_token_secret.encode('utf-8'))
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(
                            consumer,
                            token=token,
                            http_method=REQUEST_METHOD,
                            http_url=GET_USERINFO_URI)
    oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),
                               consumer, token)
    headers = oauth_request.to_header()

    http_code, content = http.get(GET_USERINFO_URI, headers=headers)
    #print http_code, content
    if http_code != 200:
        return None

    if 'errorCode' in content:
        return None

    #{"BriefUser":{"id":"11686668","constellation":0,"sex":true,"profilePictureUrl":"http://ommon/male.png",
    # "name":"ZTEU880E11686668","userName":"NM11686668","emailStatus":"false","mobileStatus":"false",
    # "status":"Visitor","mobile":"","email":"","gameBalance":"0"}}
    obj = json.loads(content)

    return {
        'openid': obj['BriefUser']['id'],          # 平台标识
        'openname': obj['BriefUser']['userName'],  # 平台昵称
    }


def payment_verify(req, params=None):
    """支付回调验证，app_order_id为自定义
    Args:
        params: 字典参数数据
            notifyId:     回调通知ID（该值使用系统为这次支付生成的订单号）
            partnerOrder: 开发者订单号（客户端上传）
            productName:  商品名称（客户端上传）
            productDesc:  商品描述（客户端上传）
            price:        商品价格(以分为单位)
            count:        商品数量（一般为1）
            attach:       请求支付时上传的附加参数（客户端上传）
            sign:         签名
    """
    if not params:
        params = {
            'notifyId': req.get_argument('notifyId', ''),
            'partnerOrder': req.get_argument('partnerOrder', ''),
            'productName': req.get_argument('productName', ''),
            'productDesc': req.get_argument('productDesc', ''),
            'price': req.get_argument('price', ''),
            'count': req.get_argument('count', ''),
            'attach': req.get_argument('attach', ''),
            'sign': req.get_argument('sign', ''),
        }

    sign_keys = ('notifyId', 'partnerOrder', 'productName', 'productDesc',
                 'price', 'count', 'attach')
    sign_values = ('%s=%s' % (k, params[k]) for k in sign_keys)
    sign_data = '&'.join(sign_values).encode('utf-8')

    if not utils.rsa_verify_signature(APP_RSA_PUBLIC_KEY, sign_data, params['sign']):
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['partnerOrder'],        # 自定义定单id
        'order_id': params['notifyId'],                # 平台定单id
        'order_money': float(params['price']) / 100,   # 平台实际支付money 单位元
        'uin': '',                                     # 平台用户id
        'platform': PLATFORM_NAME,                     # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    print login_verify('ca6a5299d156ad6fe652fdc156d8f032', '347a5e0c8235e90a8ad09d72348ccf85')

