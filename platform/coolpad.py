# coding: utf-8

import json
import urllib
from helper import http
from helper import utils

__VERSION__ = '1.2.2'
PLATFORM_NAME = 'coolpad'
APP_ID = '111111111'
APP_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxx'
REDIRECT_URI = APP_KEY  # 这个参数是由平台分配的, 不是固定值
PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIICWwIBAAKBgQCPfZ+S7YiqCmLW+hp2v9gxO70i73FUSaIkK/oHsZTbQo2p5g27
r8vil3MYqfu0fDEvMwjYwDYHrBZNt2h8LuyQzo7ySpDHgooUNmnx6gx8dAm+fcyt
6MBLlFpA2QcOZNV5Towtjq4UjTR/FgQZ5MaTndFM0h9auczXjO+PEkXDjwIDAQAB
AoGAVkjTWTXvFVkzgFRa74eDSG/E1yom+ulgT+IF8vRtL8AAkebd4TvgHXy24GDv
E+QOa3SD4FsM4mYv70HX2b0Z0T7HAoPSQOrcjlRDGw3RqxXUD4ABsa7shRHehl+2
r8ALbl9HfClu1pCY0J57Q00IQfhhAv7DdFDjbpiPN94KhQECQQDO5d3V3k2e/EaW
o0VSVQLM17I/7wHDjFvCZIkKKfa2ZNfnyw/+YHdDkYnuu+8Bhym355uzWd+bj+VC
GPSUuWGBAkEAsYtv1fuBb7vqu9lPIQYkYjhiwTGfOjCoB9O+EZII80UpxfksQ73Y
bkInNaOHQ9vX4kTLqGEZGsVW4Ek1kTWNDwJAME4Atf8Z9kWGIYNrGubYKYUui7i8
m7A4eDFKwYG8pSb0NZz2Vfilv7PKFV/xVFT/S32an4wbJdG5v+3dpJ+HgQJAc+9U
cQuRow+3oUCu3iavnX+qZPNtQUdCghHvfHO66ngQZhlmoTmX2a/TAMCu9E3bdAJu
Zp45EXUpXL4Rf6fTWwJADaafv7FlNZeHLhr2/NmAicknBvhbi/jGGUDXuqVcW4Ny
CO3mWdzUfu/F5Qc6MBk8AzbRaVcvglaJh43yKJJG8Q==
-----END PRIVATE KEY-----"""
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCvTWLYMBVxqdmWXrjKuVNVK+ql
MdfFPzxsJ7cM5M92ArcnaAqk9C4VFJqhl35eTNNuQwE81+FQmS+WY1ghdPq3Df92
bTi+qqCv4OUWouV8gUZQ+3vQPLWHQVyY2MxxHcm2Qqfzu8qXPfOmUABNl1Viex3Q
T+gR7HopgUYZzpTjoQIDAQAB
-----END PUBLIC KEY-----"""
GET_ACCESS_TOKEN_URI = 'https://openapi.coolyun.com/oauth2/token'
GET_USER_URI = 'https://openapi.coolyun.com/oauth2/api/get_user_info'
#CREATE_PAY_ORDER_URL = 'http://pay.coolyun.com:6988/payapi/order'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'SUCCESS',
    1: 'FAILURE',
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
        }
    authorization_code = params['session_id']
    access_token_data = get_access_token(authorization_code)
    # print access_token_data
    if not access_token_data:
        return None

    return {
        'openid': access_token_data['openid'],              # 平台用户ID
        'openname': access_token_data['openid'],            # 平台用户名字
        'access_token': access_token_data['access_token'],  # access_token
    }


def get_access_token(authorization_code):
    """通过code获得token
    Args:
        authorization_code: authorization_code
    Returns:
        access_token
    """
    query_str = urllib.urlencode({
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'client_id': APP_ID,
        'client_secret': APP_KEY,
        'code': authorization_code,
    })
    url = '%s?%s' % (GET_ACCESS_TOKEN_URI, query_str)
    try:
        http_code, content = http.get(url)
        # print http_code, content
    except:
        return None

    if http_code != 200:
        return None

    # {"openid":"103400","refresh_token":"0.11fae3b9fbb74","access_token":"0.e.c63"}
    obj = json.loads(content)
    if not obj.get('access_token'):
        return None

    return obj

# def get_user_info(access_token, openid):
#     """通过code获得token
#     Args:
#         authorization_code: authorization_code
#     Returns:
#         access_token
#     """
#     query_str = urllib.urlencode({
#         'access_token': access_token,
#         'oauth_consumer_key': APP_ID,
#         'openid': openid,
#     })
#     url = '%s?%s' % (GET_ACCESS_TOKEN_URI, query_str)
#     try:
#         http_code, content = http.get(url)
#     except:
#         return None
#
#     if http_code != 200:
#         return None
#
#     # {"rtn_code":"0","sex":"1","nickname":"发一个12","brithday":"1999-09-19"}
#     obj = json.loads(content)
#     return obj


def payment_create_order(params):
    """创建支付订单
    """
    return {}


def payment_verify(req, params=None):
    """支付验证
    Args:
        params: 回调字典数据
            sign: 签名
            transdata: 票据，JSON格式
                transtype: 交易类型  0–支付交易
                cporderid: 商户订单号 可选
                transid:   计费支付平台的交易流水号
                #appuserid: 用户在商户应用的唯一标识
                appid:     游戏id    String(20)    平台为商户应用分配的唯一代码
                waresid:   商品编码    integer    必填    平台为应用内需计费商品分配的编码
                feetype:   计费方式    integer    计费方式，具体定义见附录
                money:     交易金额    Float(6,2)   本次交易的金额
                currency:  货币类型以及单位RMB – 人民币（单位：元）
                result:    交易结果 0–交易成功 1–交易失败
                transtime: 交易完成时间 yyyy-mm-dd hh24:mi:ss
                cpprivate: 商户私有信息  可选    商户私有信息
                paytype:   支付方式    integer    可选    支付方式，具体定义见附录
    """
    if not params:
        params = {
            'sign': req.get_argument('sign', ''),
            'transdata': req.get_argument('transdata', ''),
            'signtype': req.get_argument('signtype', 'RSA'),
        }
    sign = utils.force_str(params['sign'])
    transdata = utils.force_str(params['transdata'])

    if not sign or not transdata:
        return RETURN_DATA, None

    if not utils.rsa_verify_signature(PUBLIC_KEY, transdata, sign, md='md5'):
        return RETURN_DATA, None

    data = json.loads(transdata)
    # 按接受成功处理
    if int(data['result']) != 0:
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    pay_data = {
        'app_order_id': data['cporderid'],                # 自定义定单id
        'order_id': data['transid'],                      # 平台定单id
        'order_money': float(data['money']),              # 平台实际支付money 单位元
        'uin': data.get('appuserid', ''),                 # 平台用户id
        'platform': PLATFORM_NAME,                        # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    params = {'session_id': '4.f02efb2f9c5c1c0de30ace168a51cdcd.c8e66c5bb4a58591ba2972a30ca776a8.1419597824908'}
    #print login_verify('', params)
    params = {'signtype': u'RSA'}
    params['transdata'] = '{"appid":"3000777425","count":1,"cporderid":"dt06aaa064-06-2-1419929824","cpprivate":"cpprivateinfo123456","currency":"RMB","feetype":0,"money":0.10,"paytype":4,"result":0,"transid":"32021412301657170095","transtime":"2014-12-30 16:59:06","transtype":0,"waresid":1}'
    params['sign'] = 'AHYojoHbbkoXLYQuMS8/DcWoBIk2w9j4V6uYTXHEYcyedxG59tEykpwJ583WiUyM4dIdsahmnTXLIjd1pQgB6/oXzDYvRwXw8HCtyCuul0p+79ElXpeTLAWIODARSqdBwFZA6j7HtP+uTTVV+TDwt4ZT2QxwtMvaijRpGAn0MR8='
    print payment_verify('', params)


