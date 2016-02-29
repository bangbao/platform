# coding: utf-8

import json
import urllib
from helper import http
from helper import utils

PLATFORM_NAME = 'wanpu'
PRODUCT_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxx'
VERIFY_LOGIN_URL = 'http:  gameproxy.xinmei365.com/game_agent/checkLogin'
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
            'user_id': req.get_argument('user_id', ''),
            'nickname': req.get_argument('nickname', ''),
            'new_channel': req.get_argument('new_channel', ''),
        }
    token = params['session_id']
    userId = params['user_id']
    productCode = params['nickname']
    channel = params['new_channel']

    query_str = urllib.urlencode({
        'userId': userId,
        'channel': channel,
        'token': token,
        'productCode': productCode 
    })

    url = '%s?%s' % (VERIFY_LOGIN_URL, query_str)
    http_code, content = http.get(url)

    if http_code != 200:
        return None
    
    obj = json.loads(content)
    if obj != True:
        return None
   
    return {
        'openid': userId,          # 平台用户ID
        'openname': userId,        # 平台用户名字
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            orderId:      订单ID
            price:        充值金额，整数，单位分，整数
            channelCode:  渠道编码 该字段内容已经Base64编码过，需decode后使用
            callbackInfo: 充值时游戏客户端传入的信息
            sign:         签名，值为MD5(orderId+price+callbackInfo+productSecret);productSecret即产品密钥
            注：验证签名的时候callbackInfo不能decode，否则会造成签名不正确。
        params: 测试专用
    """
    if not params:
        params = {
            'orderId': req.get_argument('orderId', ''),
            'price': req.get_argument('price', ''),
            'channelCode': req.get_argument('channelCode', ''),
            'callbackInfo': req.get_argument('callbackInfo', ''),
            'sign':req.get_argument('sign',''),
        }

    sign_str = '%s%s%s%s' % (params['orderId'], params['price'], params['callbackInfo'], PRODUCT_SECRET)
    new_sign = utils.hashlib_md5_sign(sign_str)
    if new_sign != params['sign']:
        return RETURN_DATA, None
    
    pay_data = {
        'app_order_id': params['callbackInfo'],         # 自定义定单id
        'order_id': params['orderId'],                  # 平台定单id
        'order_money': float(params['price']) / 100,    # 平台实际支付money 单位元
        'uin': '',                                      # 平台用户id
        'platform': PLATFORM_NAME,                      # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    #print login_verify('540683828226441ab111194b2d2e3d0f')
    #params = {'user_id':'242964320','money':'1','order_no':'GP140903181559832144','sign':'8c707850b10cf11142614482463440a6','dd':'cc'}
    params = {'sign':'xx'}
    print payment_verify('', params)
