# coding: utf-8

import urllib
import hashlib
from helper import http

# 无正式参数
__VERSION__ = 'V1.2.0'
PLATFORM_NAME = 'ewan'
# 测试配置
# APP_ID = '10008'
# PACKET_ID = '10004'
# APP_KEY = 'xxxxxxxxxx'
# SIGN_KEY = 'xxxxxxxxxxx'
#PRD_LOGIN_VERIFY = 'http://test.sdk.123cw.cn/UnionLogin/verifyToken'
# 正式配置
APP_ID = '10000'
PACKET_ID = '10001'
APP_KEY = 'xxxxxxxxxxxxxxxxxxx'
SIGN_KEY = 'xxxxxxxxxxxxxxxxxxxx'
PRD_LOGIN_VERIFY = 'http://unionlogin.123cw.cn/verifyToken'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: '1',
    1: '100',  # ‘100’表示签名错误，'101'表示未知错误
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
    token = params['session_id']
    openid = params['user_id']

    # sign_str = '%s|%s|%s' % (openid, token, APP_KEY)
    # query_str = urllib.urlencode({
    #     'openid': openid,
    #     'token': token,
    #     'sign': hashlib.md5(sign_str).hexdigest(),
    # })
    # url = '%s?%s' % (PRD_LOGIN_VERIFY, query_str)
    # http_code, content = http.get(url, timeout=2)
    # #print http_code, content
    # if http_code != 200:
    #     return None
    #
    # if content != 'success':
    #     return None

    return {
        'openid': openid,                      # 平台标识
        'openname': params['nickname'],        # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            serverid:   游戏服务器ID
            custominfo: 客户端传入的自定义数据
            openid:     合作方账号唯一标识
            ordernum:   订单  ID, 益玩订单系统唯一号
            status:     订单状态1 ,1  为成功, , 其他为失败
            paytype:    充值类型
            amount:     成功充值金额 ，单位为分
            errdesc:    充值失败错误码 ，成功为空
            paytime:    充值成功时间 ,yyyyMMddHHmmss
            sign:       所有参数y +appkey的签名拼串:
                        serverid值|custominfo值|openid值|ordernum值|status值|
                        paytype值|amount值|errdesc值|paytime值|appkey
        params: 测试专用
    """
    if not params:
        params = {
            'serverid': req.get_argument('serverid', ''),
            'custominfo': req.get_argument('custominfo', ''),
            'openid': req.get_argument('openid', ''),
            'ordernum': req.get_argument('ordernum', ''),
            'status': req.get_argument('status', 0),
            'paytype': req.get_argument('paytype', ''),
            'amount': req.get_argument('amount', ''),
            'errdesc': req.get_argument('errdesc', ''),
            'paytime': req.get_argument('paytime', ''),
            'sign': req.get_argument('sign', ''),
        }

    # 平台支付的失败的回调订单直接返回
    if int(params['status']) != 1:
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    sign_sorted_keys = ('serverid', 'custominfo', 'openid', 'ordernum', 'status',
                        'paytype', 'amount', 'errdesc', 'paytime')
    sign_values = [params[key] for key in sign_sorted_keys]
    sign_values.append(APP_KEY)
    # 没有中文，不用encode utf-8
    sign_str = '|'.join(sign_values)
    new_sign = hashlib.md5(sign_str).hexdigest()
    if new_sign != params['sign']:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['custominfo'],             # 自定义定单id
        'order_id': params['ordernum'],                   # 平台定单id
        'order_money': float(params['amount']) / 100,     # 平台实际支付money 单位元
        'uin': params['openid'],                          # 平台用户id
        'platform': PLATFORM_NAME,                        # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    print login_verify('34684388a97f284e264dc548e7d2582626834f840311c9ca', '123231')
    data = {'gid': 62, 'session_key': 'a1e912a708b9f9a669eca53a4b1180822d8fee58e01d63552b0178e3da84b614',
            'user_id': '8411626'}
    # sign = '31474948ac1926d155bc837885d6a296'
    #print generate_sougou_sign(data, '862653da5865293b1ec8cc1cab258cbc51acc8')


