# coding: utf-8

import time
import json
import urllib
import hashlib
from helper import http
from helper import utils

PLATFORM_NAME = 'zhangyue'
APP_ID = 'xxxxxxxxxxxxxxxxxxxxx'
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQDPrTifhj7qSsQGWXLElEKoQrGrXnmE7qbVD2XaR4Cd+ClK+EWd
WDh5vIccRyEQQ9uhJ3BNvWZqm2e/aVnSncYOUsD4QO4+SVQqgu78O4XYbykmaxs1
QmBq4D1Y/yLyh9Zy4vBZrbk2+nXcR1OjJfT0tBIeZNGEycnTbMhgEYHsowIDAQAB
AoGBALoJXnPo+ms/VqKpdloKxjucozP0ib8/Wkv6Yy9KZjkcmUEDbrko0k6bSB1Y
ypGbeB/BCKVbSWeulx2s7j3x//wvkOalOmd7Z4DyUyWzCu3wQfwc/E3NnDIPbFf3
ND4sutvuar76px5Pm13gQQ6YfDF9OQZ7E+fm+01hYNUTUBFBAkEA4mdd6fTG4ole
ZyWINZ4v/jdm870+LKzFPHFLWQ+qiiEnqvg1YYXteeDYxfYML4tnJaRmyNC8SJBp
P+dJ+Ov9aQJBAOrTJfkhbGwmwFgwZbX7VByGLg3/HpVIe7XW3sQTOQ5lWmNIwPmw
d0szkyTbRCPWVOpJNj1eUCP/ttTAViSz/CsCQHvhu42MllbWe4VNEB7mk7QydG7i
GecwEixkgaoV3GcAhUgT0IGwWqTZ10Nawogxaxs5vdQcAyphenWxBNTjrCECQFSg
F3U6yFoJdRPTDTSSCHPnHz3IDPt7jamwb8N1sgAwImzZUUIqiDM/uO11X48StLNi
AvwGuxbeFsOBNQoxGtUCQQCWAxFusDFY0LfUizmXYxbtFiQnRokoz9PNcqjcx6PH
SfJMuC9iWLj0wXYDVlZpxV0H0s4jLxSlcLNiXbIxM85J
-----END RSA PRIVATE KEY-----"""
#DEV_LOGIN_VERIFY = 'https://59.151.100.36:8443/api/v1/login/verify'
AUTHCODE_VERIFY = 'https://uc.zhangyue.com/open/token/check'
USERINFO_VERIFY = 'https://uc.zhangyue.com/open/user/info'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'success',
    1: 'failure',
}


def login_verify(req, params=None):
    """登录验证
    平台数据格式
        URI: /open/token/check
        参数:
            app_id: 应用ID
            open_uid: 掌阅用户UID
            authorization_code': authorization_code
            timestamp': 时间戳
            sign_type': RSA or MD5
            sign: 签名
            version': API版本
        返回:
            {
                "code":状态码
                       0:'成功',
                       30200:'签名无效',
                       30202:'应用非法',
                       30201:'授权码无效',
                "msg": "错误信息",
                "body":
                {
                    "open_uid":"掌阅用户的UID",
                    "access_token":"访问令牌",
                    "expires_in":"过期时间, 单位秒",
                    "refresh_token":"刷新令牌",
                    "refresh_expires_in":"过期时间, 单位秒",
                }
            }
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
    authorization_code = params['session_id']
    open_uid = params['user_id']

    post_data = {
        'app_id': APP_ID,
        'open_uid': open_uid,
        'access_token': authorization_code,
        'timestamp': int(time.time()),
        'sign_type': 'RSA',
        'version': '1.0',
    }
    post_data['sign'] = generate_rsa_sign(post_data, PRIVATE_KEY)

    query_str = urllib.urlencode(post_data)
    http_code, content = http.post(AUTHCODE_VERIFY, query_str, timeout=5)
    #print http_code, content
    if http_code != 200:
        return None

    obj = json.loads(content)
    if obj['code'] != 0:
        #print obj['msg']
        return None

    return {
        'openid': open_uid,          # 平台用户ID
        'openname': open_uid,        # 平台用户名字
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            merId: 商户ID，由掌阅分配
            appId: APPID
            transData: json格式数据
                merId:        商户ID，由掌阅分配
                appId:        Appid
                orderId:      掌阅订单号
                merOrderId:   商户订单
                payAmt:       订单金额， 单位元
                transTime:    交易日期格式：yyyyMMddHHmmss
                orderStatus:  订单状态：1 支付成功，其他失败
                errorCode:    错误码
                errorMsg:     错误信息
                rechargeType: 充值类型
                md5SignValue: MD5签名：签名方式为MD5(merId|appId|orderId|payAmt)
        params: 测试专用
    """
    if not params:
        params = {
            'merId': req.get_argument('merId', ''),
            'appId': req.get_argument('appId', ''),
            'transData': req.get_argument('transData', ''),
        }
    try:
        params = json.loads(params['transData'])
    except:
        return RETURN_DATA, None

    if int(params['orderStatus']) != 1:
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    sign_str = '%s|%s|%s|%s' % (params['merId'], params['appId'], params['orderId'], params['payAmt'])
    new_sign = hashlib.md5(sign_str).hexdigest()

    if new_sign != params['md5SignValue']:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['merOrderId'],       # 自定义定单id
        'order_id': params['orderId'],              # 平台定单id
        'order_money': float(params['payAmt']),     # 平台实际支付money 单位元
        'uin': '',                                  # 平台用户id
        'platform': PLATFORM_NAME,                  # 平台标识名
    }
    return RETURN_DATA, pay_data


def generate_rsa_sign(params, private_key):
    """生成签名
    Args:
        params: 要签名的字典数据
        private_key: 私钥
    Returns:
        rsa方式私钥签名
    """
    sorted_items = sorted(params.iteritems())
    sign_values = ['%s=%s' % (k, v) for k, v in sorted_items if v]
    sign_str =  '&'.join(sign_values)

    return utils.rsa_private_sign(private_key, sign_str)

# 
# def refresh_token(open_uid, refresh_token):
#     """刷新令牌
#     URI: /open/token/refresh
#     Args:
#         app_id: 应用ID
#         open_uid: 掌阅用户UID
#         refresh_token': 刷新令牌
#         timestamp': 时间戳
#         sign_type': RSA or MD5
#         sign: 签名
#         version': API版本
#     Returns:
#         {
#             "code":状态码
#                    0:'成功',
#                    30200:'签名无效',
#                    30202:'应用非法',
#                    30214:'刷新令牌无效',
#                    30215:'刷新令牌过期'
#             "msg": "错误信息",
#             "body":
#             {
#                 "open_uid":"掌阅用户的UID",
#                 "access_token":"访问令牌",
#                 "expires_in":"过期时间, 单位秒",
#                 "refresh_token":"刷新令牌",
#                 "refresh_expires_in":"过期时间, 单位秒",
#             }
#         }
#     """
#     pass
# 
# 
# def get_user_info(open_uid, access_token):
#     """查询用户信息
#     URI: /open/account/info
#     Args:
#         app_id: 应用ID
#         open_uid: 掌阅用户UID
#         access_token': 访问令牌
#         timestamp': 时间戳
#         sign_type': RSA or MD5
#         sign: 签名
#         version': API版本
#     Returns:
#         {
#             "code":状态码
#                    0:'成功',
#                    30200:'签名无效',
#                    30202:'应用非法',
#                    30212:'访问令牌无效',
#                    30213:'访问令牌过期'
#             "msg": "错误信息",
#             "body":
#             {
#                 "open_uid":"掌阅用户的UID",
#                 "nick":"昵称",
#                 "balance":"余额",
#             }
#         }
#     """
#     pass


if __name__ == '__main__':
    print login_verify('1b2822a854be08f4582708d5e7681305', 'b1f81139f83ba996f1ca26f05a304fe8', )
    data = {'gid': 62, 'session_key': 'a1e912a708b9f9a669eca53a4b1180822d8fee58e01d63552b0178e3da84b614',
            'user_id': '8411626'}


