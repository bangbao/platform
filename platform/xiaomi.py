# coding: utf-8

import json
import urllib
from helper import http
from helper import utils

__VERSION__ = 'v4.3.4'
PLATFORM_NAME = 'xiaomi'
APP_ID = '111111111111111111111111'
APP_KEY = '111111111111'
APP_SECRET = 'xxxxxxxxxxxxxxxxx+A=='
VERIFY_SESSION_URL = 'http://mis.migc.xiaomi.com/api/biz/service/verifySession.do'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: {'errcode' : 200, 'errMsg' : 'sucess'},
    1: {'errcode': 1525, 'errmsg' : 'sign error'},
}


def login_verify(req, params=None):
    """登录验证
    Args:
        req: request封装，以下是验证所需参数
            session_id: 32 位字符串
        params: 测试专用
    Returns:
        平台相关信息(openid必须有)
    """
    if not params:
        params = {
            'session_id': req.get_argument('session_id', ''),
            'user_id': req.get_argument('user_id', ''),
        }
    uid = params['user_id']
    session = params['session_id']

    get_data = {
        'appId': APP_ID,
        'uid': uid,
        'session': session,
    }
    get_data['signature'] = xiaomi_make_sign(get_data)
    url = '%s?%s' % (VERIFY_SESSION_URL, urllib.urlencode(get_data))
    http_code, content = http.get(url)
    #print http_code, content
    if http_code != 200:
        return None

    result = json.loads(content)
    if result['errcode'] != 200:
        return None

    return {
        'openid': uid,                # 平台标识
        'openname': uid,              # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            appId:            APP_ID
            cpOrderId:        开发商订单 ID
            cpUserInfo:       开发商透传信息
            uid:              用户 ID
            orderId:          游戏平台订单 ID
            orderStatus:      订单状态 TRADE_SUCCESS 代表成功
            payFee:           支付金额,单位为分,即 0.01 米币
            productCode:      商品代码
            productName:      商品名称
            productCount:     商品数量
            payTime:          支付时间,格式 yyyy-MM-dd HH:mm:ss
            orderConsumeType: 订单类型:10:普通订单 11:直充直消订单
            signature:        签名
        params: 测试专用
    """
    if not params:
        params = {
            'appId': req.get_argument('appId', ''),
            'cpOrderId': req.get_argument('cpOrderId', ''),
            'cpUserInfo': req.get_argument('cpUserInfo', ''),
            'uid': req.get_argument('uid', ''),
            'orderId': req.get_argument('orderId', ''),
            'orderStatus': req.get_argument('orderStatus', ''),
            'payFee': req.get_argument('payFee', ''),
            'productCode': req.get_argument('productCode', ''),
            'productName': req.get_argument('productName', ''),
            'productCount': req.get_argument('productCount', ''),
            'payTime': req.get_argument('payTime', ''),
            'orderConsumeType': req.get_argument('orderConsumeType', ''),
            'signature': req.get_argument('signature', ''),
            'partnerGiftConsume': req.get_argument('partnerGiftConsume', '')
        }
    if not params['partnerGiftConsume']:
        del params['partnerGiftConsume']

    if params['orderStatus'] != 'TRADE_SUCCESS':
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    new_sign = xiaomi_make_sign(params)
    if new_sign != params['signature']:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['cpOrderId'],            # 自定义定单id
        'order_id': params['orderId'],                  # 平台定单id
        'order_money': float(params['payFee']) / 100,   # 平台实际支付money 单位元
        'uin': params['uid'],                           # 平台用户id
        'platform': PLATFORM_NAME,                      # 平台标识名
    }
    return RETURN_DATA, pay_data


def xiaomi_make_sign(data):
    """制作签名 按字母顺序排序 使用hmac-sha1
    Args:
        data: 要签名的字典数据
    Returns:
        hmac-sha1签名
    """
    # 所有的必选参数都必须参与签名，空串也参与签名
    exclude_keys = ('signature', 'orderConsumeType')
    sorted_items = sorted(data.iteritems())
    msg_list = ("%s=%s" % (key, value)
                for key, value in sorted_items if key not in exclude_keys)
    msg = '&'.join(msg_list)
    return utils.hmac_sha1_sign(APP_SECRET, msg)


if __name__ == '__main__':
    print login_verify('', {'user_id': '59577766', 'session_id': '0opZK4UwvNwhRu3a'})
    #print payment_verify('', {'orderId': u'21139764002334905623', 'cpOrderId': u'h12742989-h1-1-1397640020', 'payFee': u'100', 'uid': u'13817493', 'orderConsumeType': '', 'productCount': u'1', 'productName': u'', 'orderStatus': u'TRADE_SUCCESS', 'cpUserInfo': u'h12742989-h1-1-1397640020', 'appId': u'24957', 'payTime': u'2014-04-16 17:20:25', 'productCode': u'01', 'signature': u'ef44ac770d4f5b3299b7a4c7ca18cf1028b80535'})


