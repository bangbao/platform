# coding: utf-8

import json
import urllib
from helper import http
from helper import utils

__VERSION__ = '3.4.2'
PLATFORM_NAME = 'haima'
APP_ID = '111111111111111111'
APP_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCM33PU18X1pk8xTIkrtnqXShEJIbEefwdFZ9u29WS/vXyOfdrh
oD/Tvnd32nBSjCBQe6UEkofYHhAHvp5iONgy9vZzNo7iskYgQw72uAiPIHrx9S2x
r8MJKAxMQripsrQxM/7/W7JanWokr2i+d1v66cQ5aUfgaD+kvRMAKeNotwIDAQAB
AoGALIOrkXVBa5dK7PQXYEXARTA1Y+JOmqlfPdJMvmqalHAm/MvOL3+4y4sjKy9O
UPdQer4nbeNzo5oUTK4yVC1MO4l5J/oucIvPIszBHUXamGlJ7sLFspfpGEAoTGhE
3TosrYTY/J3uTw67YFo0IlqN08uYI79lmDwmgxeb5dF2HlECQQD9gcVJvAIlOJ+r
pamPK01h+tRgTk0VO0mdR0pnGX1lbtQcgOSt+M1hvGN96qgvFu7sTPdnp83yakq0
NNPMu6RvAkEAjkIdOfGWUMGE8bPqr6V3AAal7FbA9prIic+YJTVDeszwY2ASXDMn
lOzlxupoCNoAfQpI2R+2RPIaKOwM3770OQJAd1Qbit6938lsl36Odv76GPHaAE87
R5A10ZvaMPe1qAZoP9aITj/8ZVIpPv8zFZ9k7cQ4/QjnD4HrEjJ/tDJrbwJAMXTK
tFpI58pfbage7vGXbWriREfkzdcB4OdK/aSG0SpuaB3+RA+Es0GooH7drDYd9Vqd
+N4Nf+qrLY7i6uZ4AQJBAM96vevY75SPQHt4tqFVj217gRDNfWf9YFanXj9ZW9uF
Ku3LlvnjAo2y65mYvDZ4Wr9RILK7c/Kb6PHmLVKo+00=
-----END RSA PRIVATE KEY-----"""
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCntAGVDywe+QBcswFQQZnkUpjD
iyCxbLWi1VcBsBfKi3JhSMZlt3mF0pipaSlt8wRd2umEY8zDnsN+OeXClKJMRXMJ
iFEtz6EmCK6b0VB7HfBoMfEngp71uR2G9zqFJhXEEyx6PWZKmkTP77t+26BeRnjr
970zmiIP6m9XvKyYgQIDAQAB
-----END PUBLIC KEY-----"""
GET_USERINFO_URL = 'http://ipay.iapppay.com:9999/payapi/tokencheck'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'SUCCESS',
    1: 'FAILURE',
}


def login_verify(req, params=None):
    """登录验证
    Args:
        req: request封装，以下是验证所需参数
            session_id: 固定参数，默认平台sid, 具体每个平台含义与前端商定
            user_id: 固定参数，默认表示平台ID, 具体每个平台含义与前端商定
            nickname: 固定参数 默认表示平台昵称, 具体每个平台含义与前端商定
        params: 测试专用
    Returns:
        平台相关信息(openid必须有)
    """
    if not params:
        params = {
            'session_id': req.get_argument('session_id', ''),
            'nickname': req.get_argument('nickname', ''),
        }
    logintoken = params['session_id']
    #nickname = params['nickname']

    transdata = json.dumps({'appid': APP_ID, 'logintoken': logintoken})
    post_data = urllib.urlencode({
        'transdata': transdata,
        'sign': utils.rsa_private_sign(APP_KEY, transdata, algo='md5'),
        'signtype': 'RSA',
    })
    http_code, content = http.post(GET_USERINFO_URL, post_data)
    #print http_code, urllib.unquote(content)
    if http_code != 200:
        return None

    data = dict(utils.parse_cgi_data(content))
    result = urllib.unquote(data['transdata'])
    data = json.loads(result)
    if data.get('code', 0) != 0:
        return None

    return {
        'openid': data['userid'],                # 平台标识
        'openname': data['loginname'],           # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            transdata: json格式数据
                transtype:    交易类型
                cporderid:    商户订单号
                transid:      计费支付平台的交易流水号
                appuserid:    用户在商户应用的唯一标识
                appid:        平台为商户应用分配的唯一代码
                waresid:      平台为应用内需计费商品分配的编码
                feetype:      计费方式
                money:        本次交易的金额, 单位元
                currency:     货币类型
                result:       交易结果 0 成功 1 失败
                transtime:    交易时间格式：yyyy-mm-dd hh24:mi:ss
                cpprivate:    商户私有信息 可选
                paytype:      支付方式 可选
            sign: 签名
            signtype: RSA
        params: 测试专用
    """
    if not params:
        params = {
            'transdata': req.get_argument('transdata', ''),
            'sign': req.get_argument('sign', ''),
        }
    sign = utils.force_str(params['sign'])
    transdata = utils.force_str(params['transdata'])

    if not sign or not transdata:
        return RETURN_DATA, None

    if not utils.rsa_verify_signature(PUBLIC_KEY, transdata, sign, md='md5'):
        return RETURN_DATA, None

    transdata = json.loads(transdata)
    # 按接受成功处理
    if int(transdata['result']) != 0:
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    pay_data = {
        'app_order_id': transdata['cporderid'],            # 自定义定单id
        'order_id': transdata['transid'],                  # 平台定单id
        'order_money': float(transdata['money']),          # 平台实际支付money 单位元
        'uin': '',                                         # 平台用户id
        'platform': PLATFORM_NAME,                         # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    print login_verify('', {'session_id': '07d72e5200cb5c0031d988e618d90d5b'})


