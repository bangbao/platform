# coding: utf-8

import json
import time
import urllib
from helper import http
from helper import utils

__VERSION__ = '1.3.1.1'  # 登录版本号
PLATFORM_NAME = 'huawei'
CPID = '111111111111111111'
APP_ID = '11111111'
PAY_ID = '11111111111111111111111'
PAY_RSA_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAKc2F87Cvol4nBnXKrTu0WNcuZa/m8IGx
k4+YP3+fYHXfx9ZBEdqnUo+zDz6CPqEICe1xRFtdrrMCgrD1+A0picCAwEAAQ==
-----END PUBLIC KEY-----"""
PAY_RSA_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIBUwIBADANBgkqhkiG9w0BAQEFAASCAT0wggE5AgEAAkEApzYXzsK+iXicGdcqt
O7RY1y5lr+bwgbGTj5g/f59gdd/H1kER2qdSj7MPPoI+oQgJ7XFEW12uswKCsPX4D
SmJwIDAQABAkAjVEuNdRo7A4+/6fVtCzSUkOfpkQyA31uQ9p8Zq2arQxsjuPLTVLk
UrUPzJzi5Gk5oebov0u4HGsncLi+g2PlhAiEA9oDp9ctskNMGNBjkbPTjAJ81nMWk
B27Hu9DSY1efdnECIQCtpy1JFdsZZlXZTXTz/84hpRSHJYPZfXAgeD7/FIYiFwIgG
qrjpLW3LwvFVgmDXM45aK3QrP8suakgbo8u05R9KeECIHOf7dpNEC7wYdcn6OiSej
kSxwFZrFoDWMZ16lRD4TAPAiBJJPK9ASvnDHGARnKtSp8Ko+WxQkg1EwbQ2xCuuk3
ooQ==
-----END PRIVATE KEY-----"""
GET_USERINFO_URI = 'https://api.vmall.com/rest.php'
NSP_SVC = 'OpenUP.User.getInfo'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: {'result': 0},
    1: {'result': 1},
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
        }
    access_token = params['session_id']
    # user_id = params['user_id']

    post_data = urllib.urlencode({
        'nsp_svc': NSP_SVC,
        'nsp_ts': int(time.time()),
        'access_token': access_token,
    })
    http_code, content = http.post(GET_USERINFO_URI, post_data)
    # print http_code, content
    if http_code != 200:
        return None

    # {"gender":2,"languageCode":"zh","userID":"1727","userName":"chenshu","userState":1,"userValidStatus":1}
    data = json.loads(content)
    if not data.get('userID'):
        return None

    return {
        'openid': data['userID'],                            # 平台标识
        'openname': data.get('userName', data['userID']),    # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            result: 支付结果“0”，表示支付成功
            userName:   开发者社区用户名或工会用户编号
            productName: 商品名称
            payType:    支付类型
            amount:     商品支付金额 (格式为：元.角分，最小金额为分， 例如：20.00)
            orderId:    华为订单号
            notifyTime: 通知时间。 (自 1970 年 1 月 1 日 0 时起的毫秒数)
            requestId:  开发者支付请求 ID，原样返回
            bankId:     银行编码-支付通道信息:1.只有在有具体取值时才传递,具体取值请参考下文;2.商户在前台sdk中指定了urlver配置项,且取值为‘2’;
            orderTime:  下单时间 yyyy-MM-dd hh:mm:ss
            tradeTime: 交易/退款时间 yyyy-MM-dd hh:mm:ss
            accessMode: 接入方式
            spending: 渠道开销，保留两位小数，单位元。
            extReserved: 商户侧保留信息,原样返回
            sign:       RSA 签名
        params: 测试专用
    """
    if not params:
        params = {
            'body': req.request.body,
        }

    params = dict(utils.parse_cgi_data(params['body']))
    if 'sign' not in params:
        return RETURN_DATA, None

    if int(params['result']) != 0:
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    params['sign'] = urllib.unquote(params['sign'])
    params_keys = sorted((k for k, v in params.iteritems() if k != 'sign'))
    sign_values = ('%s=%s' % (k, params[k]) for k in params_keys)
    sign_data = '&'.join(sign_values)

    if not utils.rsa_verify_signature(PAY_RSA_PUBLIC_KEY, sign_data, params['sign']):
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['requestId'],       # 自定义定单id
        'order_id': params['orderId'],             # 平台定单id
        'order_money': float(params['amount']),    # 平台实际支付money 单位元
        'uin': params['userName'],                 # 平台用户id
        'platform': PLATFORM_NAME,                 # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    print login_verify('BFEsZqBuaW//9GGn1mLt+KykzfBObIy6V3eN20ufoNiAERl33oVGzlN5TE5qeA==', 123)

