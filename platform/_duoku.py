# coding: utf-8

import json
import urllib
import hashlib
from helper import http

PLATFORM_NAME = 'duoku'
APP_ID = '1111'
APP_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxx'
APP_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
VERIFY_SESSION_URI = 'http://sdk.m.duoku.com/openapi/sdk/checksession'
QUERY_PAYMENT_URI = 'http://sdk.m.duoku.com/openapi/sdk/duokoo_card_result'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'SUCCESS',
    1: 'ERROR_SIGN',
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
    sessionid = params['session_id']
    uid = params['user_id']

    params_data = {
        'appid': APP_ID,
        'appkey': APP_KEY,
        'uid': uid,
        'sessionid': sessionid,
    }
    checksession = ''.join((APP_ID, APP_KEY, uid, sessionid, APP_SECRET))
    params_data['clientsecret'] = hashlib.md5(checksession).hexdigest()

    url = '%s?%s' % (VERIFY_SESSION_URI, urllib.urlencode(params_data))
    http_code, content = http.get(url, timeout=5)

    if http_code != 200:
        return None

    obj = json.loads(content)
    if obj['error_code'] != 0:
        return None

    return {
        'openid': uid,      # 平台标识
        'openname': uid,    # 平台昵称
    }



def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            amount:        充值成功的金额(单位:按汇率结算后的元),
            cardtype:      充值类型 0 酷币充值(账户酷币余额兑换游戏币) 1 移劢充值卡 
                                    2 联通充值卡 3 电信充值卡 101 支付宝 102 财付通
            orderid:       订单号(如 cp 未提供订单号,则传入多酷订单号)
            result:        充值结果(1:成功, 2:失败)
            timetamp:      订单完成时的 unix 时间戳
            aid:           将客户端传入的 aid 原样传回
            client_secret: 将以上 6 个参数加上secret 按顺序组成串进行MD5加密
        params: 测试专用
    Returns:
        return_data: 返回数据
            成功和失败的数据
        pay_data: 支付数据
            app_order_id: 自定义定单id
            order_id: 平台定单id
            order_money: 平台实际支付money
            uin: 平台用户id
            platform: 平台标识
    """
    if not params:
        params = {
            'amount': req.get_argument('amount', ''),
            'cardtype': req.get_argument('cardtype', ''),
            'orderid': req.get_argument('orderid', ''),
            'result': req.get_argument('result', ''),
            'timetamp': req.get_argument('timetamp', ''),
            'aid': req.get_argument('aid', ''),
            'client_secret': req.get_argument('client_secret', ''),
        }

    # 按接受成功处理
    if int(params['result']) != 1:
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    params['secret'] = APP_SECRET
    if isinstance(params['aid'], unicode):
        params['aid'] = params['aid'].encode('utf-8')

    params['aid'] = urllib.quote(params['aid'])

    pre_sign =  ('%(amount)s'
                 '%(cardtype)s'
                 '%(orderid)s'
                 '%(result)s'
                 '%(timetamp)s'
                 '%(secret)s'
                 '%(aid)s') % params
    new_sign = hashlib.md5(pre_sign).hexdigest()
    if new_sign != params['client_secret']:
        return RETURN_DATA, None

    # 不需要再次请求数据
    # query_data =  query_result(params['orderid'])
    # if not query_data or int(query_data['Amount']) < int(params['amount']):
    #     return None

    pay_data = {
        'app_order_id': params['aid'],              # 自定义定单id
        'order_id': params['orderid'],              # 平台定单id
        'order_money': float(params['amount']),     # 平台实际支付money 单位元
        'uin': '',                                  # 平台用户id
        'platform': PLATFORM_NAME,                  # 平台标识名
    }
    return RETURN_DATA, pay_data


# def query_result(order_id):
#     """查询支付购买结果
#     Args:
#         order_id: 多酷平台订单id
#     Returns:
#         查询结果
#     """
#     params_data = {
#         'appid': APP_ID,
#         'appkey': APP_KEY,
#         'orderid': order_id,
#     }
#     sign_str = ''.join((APP_ID, APP_KEY, order_id, APP_SECRET))
#     params_data['clientsecret'] = hashlib.md5(sign_str).hexdigest()
# 
#     url = '%s?%s' % (QUERY_PAYMENT_URI, urllib.urlencode(params_data))
#     http_code, content = http.get(url, timeout=5)
# 
#     if http_code != 200:
#         return None
# 
#     obj = json.loads(content)
# 
#     # 0 充值已提交 1 充值成功 2 充值失败 3 查询失败
#     if obj.get('Result') not in ('0', '1'):
#         return None
# 
#     return obj



if __name__ == '__main__':
    print login_verify('11111', 'bbbbbb')

