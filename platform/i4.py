# coding: utf-8

import json
from helper import http
from helper import utils

__VERSION__ = '1.0'
PLATFORM_NAME = 'i4'
APP_ID = '111'
APP_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
DEFAULT_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCgt4R+/A/fHEFGn8eVuKB+qRIc2gU/1BxrjXn5
A6TK0NuOSfts03BvmkH5qPIrUbRIbURKUImRxQfSQh1NQQw72KIfXVXjw2aHTj7/g+KX8xPvJfNs
W+sFx4F8svbMM4ufegTwpl5AVbHRRyMlL6jk4e3FXjW00qG3+POor4rk7wIDAQAB
-----END PUBLIC KEY-----"""
GET_USER_URL = 'https://pay.i4.cn/member_third.action'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'success',
    1: 'fail',
}


def login_verify(req, params=None):
    """爱思登陆验证
    """
    if not params:
        params = {
            'session_id': req.get_argument('session_id', ''),
            'user_id': req.get_argument('user_id', ''),
        }
    token = params['session_id']
    user_id = params['user_id']

    url = "%s?token=%s" % (GET_USER_URL, token)
    try:
        http_code, content = http.get(url)
        #print http_code, content
    except:    # 对方出现timeout, 跳过验证
        if user_id:
            return {'openid': user_id, 'openname': user_id}
        return None

    if http_code != 200:
        return None

    # {"status":0,"username":"ceshi1","userid":100001}
    result = json.loads(content)
    if result['status'] != 0:
        return None

    return {
        'openid': result['userid'],          # 平台标识
        'openname': result['username'],      # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            order_id        兑换订单号
            billno          厂商订单号
            account         通行证帐号
            amount          兑换爱思币数量
            status          0正常状态，1已经兑换过并且正常返回
            app_id          厂商应用id
            role            厂商应用角色id
            zone            厂商应用分区id
            sign            签名(RSA 私钥加密)
        params: 测试专用
    """
    if not params:
        params = {
            'order_id': req.get_argument('order_id', 0),
            'billno': req.get_argument('billno', ''),
            'account': req.get_argument('account', ''),
            'amount':req.get_argument('amount', ''),
            'status':req.get_argument('status', 0),
            'app_id':req.get_argument('app_id', ''),
            'role':req.get_argument('role', ''),
            'zone':req.get_argument('zone', ''),
            'sign':req.get_argument('sign', ''),
        }

    if not params['sign'] or not params['billno']:
        return RETURN_DATA, None

    # status 做重复判断,当不等于0 时,表示订单已处理过
    if params['status'] != '0':
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    transSign = utils.rsa_public_decrypt(DEFAULT_PUBLIC_KEY, params['sign'], max_decrypt_block=128)
    transDict = dict(utils.parse_cgi_data(transSign))

    for k, v in transDict.iteritems():
        if k == "sign":
            continue
        if v != params.get(k):
            return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['billno'],         # 自定义定单id
        'order_id': params['order_id'],           # 平台定单id
        'order_money': float(params['amount']),   # 平台实际支付money 单位元
        'uin': params['account'],                 # 平台用户id
        'platform': PLATFORM_NAME,                # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    print login_verify('34684388a97f284e264dc548e7d2582626834f840311c9ca')
