# coding: utf-8

import time
import json
import urllib
from helper import http
from helper import utils

PLATFORM_NAME = 'xmw'
APP_KEY = 'xxxxxxxxxxxxxxxxxxxxxx'
APP_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxx'
GET_ACCESS_TOKEN_URI = 'http://open.xmwan.com/v2/oauth2/access_token'
GET_USER_URI = 'http://open.xmwan.com/v2/users/me'
PAYMENT_VERIFY_URI = 'http://open.xmwan.com/v2/purchases/verify'
PAYMENT_MAKE_ORDER_URI = 'http://open.xmwan.com/v2/purchases'
GRANT_TYPE = 'authorization_code'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'success',
    1: 'fail',
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

    access_token = get_access_token(authorization_code)
    #access_token = '3468438871d7d7c35eb9a8b8e6925d56fad1154d2cec8642'
    if not access_token:
        return None

    query_str = urllib.urlencode({
        'access_token': access_token,
    })
    url = '%s?%s' % (GET_USER_URI, query_str)
    http_code, content = http.get(url)
    #print http_code, content
    if http_code != 200:
        return None

    obj = json.loads(content)

    return {
        'openid': obj['xmw_open_id'],     # 平台用户ID
        'openname': obj['nickname'],      # 平台用户名字
    }


def get_access_token(authorization_code):
    """通过code获得token
    Args:
        authorization_code: authorization_code
    Returns:
        access_token
    """
    query_str = urllib.urlencode({
        'client_id': APP_KEY,
        'client_secret': APP_SECRET,
        'grant_type': GRANT_TYPE,
        'code': authorization_code,
    })
    try:
        http_code, content = http.post(GET_ACCESS_TOKEN_URI, query_str)
    except:
        return None
    #print content
    if http_code != 200:
        return None

    obj = json.loads(content)
    return obj['access_token']


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            app_order_id:    应用订单id
            app_subject:     支付的标题
            app_description: 支付的详细内容
            app_user_id:     游戏方传入的ID，原样返回
            app_ext1:        应用扩展信息 1 原样返回 (不要有空格和符号)
            app_ext2:        应用扩展信息 2 原样返回 (不要有空格和符号)
            order_id:        XMW 返回的支付订单号
            sign_type:       定值 md5
            sign_return:     订单的参数签名。
            status:          如果支付返回成功，返回 SUCCESS 应用需要确认是 SUCCESS 才给用户加钱
            payment:         支付方式
            amount:          支付金额
        params: 测试专用
    """
    if not params:
        params = {
            'app_order_id': req.get_argument('app_order_id', ''),
            'app_subject': req.get_argument('app_subject', ''),
            'app_description': req.get_argument('app_description', ''),
            'app_user_id': req.get_argument('app_user_id', ''),
            'app_ext1': req.get_argument('app_ext1', ''),
            'app_ext2': req.get_argument('app_ext2', ''),
            'order_id': req.get_argument('order_id', ''),
            'sign_type': req.get_argument('sign_type', ''),
            'sign_return': req.get_argument('sign_return', ''),
            'status': req.get_argument('status', ''),
            'payment': req.get_argument('payment', ''),
            'amount': req.get_argument('amount', ''),
        }
    if params['status'] != "SUCCESS":
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    query_data = urllib.urlencode({
        'client_id': APP_KEY,
        'client_secret': APP_SECRET,
        'amount': params['amount'],
        'app_order_id': params['app_order_id'],
        'sign_type': params['sign_type'],    # 当前仅支持 md5
        'sign': params['sign_return'],
    })
    url = PAYMENT_VERIFY_URI % params['order_id']
    try:
        http_code, content = http.post(url, query_data, timeout=5)
    except:
        return RETURN_DATA, None
    #print content
    if http_code != 200:
        return RETURN_DATA, None

    obj = json.loads(content)
    if obj.get('status') != 'success':
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['app_order_id'],      # 自定义定单id
        'order_id': params['order_id'],              # 平台定单id
        'order_money': float(params['amount']),      # 平台实际支付money 单位元
        'uin':  '',                                  # 平台用户id
        'platform': PLATFORM_NAME,                   # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    print login_verify('34684388a97f284e264dc548e7d2582626834f840311c9ca')
    params = {
        'app_order_id': 'xx',
        'app_user_id': 'h11234567',
        'notify_url': 'http://dev.kaiqigu.net/genesis/pay-callback-xmw2/',
        'amount': 6,
        'timestamp': int(time.time()),
    }
    #print make_sign(params)


