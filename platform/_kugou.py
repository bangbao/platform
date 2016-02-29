# coding: utf-8

import json
from helper import http
from helper import utils

PLATFORM_NAME = 'kugou'
MerchantId = '11'
APP_ID = '1111'
Game_ID = '11111'
APP_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
VERIFY_SESSION_URI = 'http://sdk.game.kugou.com/index.php?r=ValidateIsLogined/CheckToken'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'SUCCESS',
    1: 'FAIL',
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

    url = '%s&token=%s' % (VERIFY_SESSION_URI, sessionid)
    http_code, content = http.get(url)
    #print http_code, content
    if http_code != 200:
        return None

    data = json.loads(content)
    if data['response']['code'] != '0':
        return None

    return {
        'openid': uid,          # 平台用户ID
        'openname': uid,        # 平台用户名字
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            orderid:     long      平台订单号（联运平台唯一订单号）
            outorderid:  String    游戏厂商订单号(游戏厂商需保证订单唯一性) (回调时url编码)
            amount:      int       充值金额(人民币)，以此值兑换游戏币。单位（元）
            username:    string    平台帐号(回调时url编码)
            status:      Int       是否扣费成功.1:成功,0:不成功
            time:        int       发起请求时间，Unix时间戳
            ext1:        String    扩展字段1,原样传回(回调时url编码)
            ext2:        String    扩展字段2,原样传回(回调时url编码)
            sign:        string    签名验证，md5后的结果小写
                md5(orderid+outorderid+amount+username+status+time+ext1+ext2+key)
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
            'orderid': req.get_argument('orderid', ''),
            'outorderid': req.get_argument('outorderid', ''),
            'amount': req.get_argument('amount', ''),
            'username': req.get_argument('username',''),
            'status': req.get_argument('status', 0),
            'time': req.get_argument('time', ''),
            'ext1': req.get_argument('ext1',''),
            'ext2': req.get_argument('ext2',''),
            'sign': req.get_argument('sign',''),
        }
    params['key'] = APP_KEY

    if int(params['status']) != 1:
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    sign_str = ('%(orderid)s'
                '%(outorderid)s'
                '%(amount)s'
                '%(username)s'
                '%(status)s'
                '%(time)s'
                '%(ext1)s'
                '%(ext2)s'
                '%(key)s') % params
    new_sign = utils.hashlib_md5_sign(sign_str)
    if new_sign != params['sign']:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['outorderid'],        # 自定义定单id
        'order_id': params['orderid'],               # 平台定单id
        'order_money': float(params['amount']),      # 平台实际支付money 单位元
        'uin': params['username'],                   # 平台用户id
        'platform': PLATFORM_NAME,                   # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    pass

