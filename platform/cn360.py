# coding: utf-8

import json
import urllib
from helper import http
from helper import utils

__VERSION__ = '1.1.2'
PLATFORM_NAME = '360'
APP_ID = '1111111'
APP_KEY = 'xxxxxxxxxxxxxxxxxxxx'
APP_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxx'
GET_USER_URI = 'https://openapi.360.cn/user/me.json'
PAYMENT_VERIFY_URI = 'https://openapi.360.cn/pay/verify_mobile_notification.json'
REDIRECT_URI = 'oob'
GRANT_TYPE = 'authorization_code'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'ok',
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
            'session_id': req.get_argument('session_id'),
        }
    access_token = params['session_id']

    query_str = urllib.urlencode({
        'access_token': access_token,
    })
    url = '%s?%s' % (GET_USER_URI, query_str)
    # 对方服务器经常timeout
    try:
        http_code, content = http.get(url, timeout=1)
        # print http_code, content
    except:
        return None
    if http_code != 200:
        return None

    # {"id": "201459001","name": "360U201459001","sex": "未知""area": ""}
    obj = json.loads(content)

    return {
        'openid': obj['id'],          # 平台用户ID
        'openname': obj['name'],      # 平台用户名字
        'access_token': access_token,  # 返回用户access_token
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            app_key:      应用 app key
            product_id:   所购商品 id
            amount:       总价,以分为单位
            app_uid:      应用内用户 id
            app_ext1:     应用扩展信息 1 原样返回
            app_ext2:     应用扩展信息 2 原样返回
            user_id:      360 账号 id
            order_id:     360 返回的支付订单号
            gateway_flag: 如果支付返回成功,返回 success应用需要确认是 success 才给用户加钱
            sign_type:    定值 md5
            app_order_id: 应用订单号 支付请求时若传递就原样返回
            sign_return:  应用回传给订单核实接口的参数 不加入签名校验计算
            sign:         签名
        params: 测试专用
    """
    if not params:
        params = {
            'app_key': req.get_argument('app_key', ''),
            'product_id': req.get_argument('product_id', ''),
            'amount': int(req.get_argument('amount', 0)),
            'app_uid': req.get_argument('app_uid', ''),
            'app_ext1': req.get_argument('app_ext1', ''),
            'app_ext2': req.get_argument('app_ext2', ''),
            'user_id': req.get_argument('user_id', ''),
            'order_id': req.get_argument('order_id', ''),
            'gateway_flag': req.get_argument('gateway_flag', ''),
            'sign_type': req.get_argument('sign_type', ''),
            'app_order_id': req.get_argument('app_order_id', ''),
            'sign_return': req.get_argument('sign_return', ''),
            'sign': req.get_argument('sign', ''),
        }

    # 当做接受成功处理
    if params['gateway_flag'] != "success":
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    # 按key自然排序
    exclude_keys = set(['sign', 'sign_return'])
    sign_keys = sorted(params.iterkeys())
    sign_values = [str(params[key]) for key in sign_keys if key not in exclude_keys and params[key]]
    sign_values.append(APP_SECRET)
    sign_str = '#'.join(sign_values)
    new_sign = utils.hashlib_md5_sign(sign_str)
    if new_sign != params['sign']:
        return RETURN_DATA, None

#     params['client_id'] = APP_KEY
#     params['client_secret'] = APP_SECRET
#     # 账单核实接口
#     url = '%s?%s' % (PAYMENT_VERIFY_URI, urllib.urlencode(params))
#     http_code, content = http.get(url, timeout=10)
#     if http_code != 200:
#         return RETURN_DATA, None
#
#     obj = json.loads(content)
#     if obj.get('ret') != 'verified':
#         return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['app_order_id'],          # 自定义定单id
        'order_id': params['order_id'],                  # 平台定单id
        'order_money': float(params['amount']) / 100,    # 平台实际支付money 单位元
        'uin': params['user_id'],                        # 平台用户id
        'platform': PLATFORM_NAME,                       # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    params = {'session_id': '52422129e27ea945bf0123cb66c4662671e764bb9bad486e'}
    print login_verify('', params)


