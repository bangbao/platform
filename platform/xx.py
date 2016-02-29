# encoding: utf-8

import time
import urllib
from helper import http
from helper import utils

__VERSION__ = '1.0.0'
PLATFORM_NAME = 'xx'
MERCHANT_ID = '1111'
APP_ID = '111111'
SERVER_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
# CLIENT_SECRET_KEY = 'xxxxxxxxxxxxx'
APP_USERINFO_URL = 'http://guopan.cn/gamesdk/verify/'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'success',
    1: 'failure',
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
    game_uin = params['user_id']
    t = int(time.time())

    query_data = {
        'game_uin': game_uin,
        'appid': APP_ID,
        'token': token,
        't': t,
    }
    sign = '%s%s%s%s' % (game_uin, APP_ID, t, SERVER_KEY)
    query_data['sign'] = utils.hashlib_md5_sign(sign)
    url = '%s?%s' % (APP_USERINFO_URL, urllib.urlencode(query_data))
    http_code, content = http.get(url)
    #print http_code, content
    if http_code != 200:
        return None

    if content != 'true':
        return None

    return {
        'openid': game_uin,                # 平台标识
        'openname': params['nickname'],    # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        params: 字典参数数据
            trade_no:       果盘唯一订单号
            serialNumber:   游戏方订单序列号
            money:          消费金额。单位是元，精确到分，如10.00
            status:         状态；0=失败；1=成功；2=失败，原因是余额不足。
            t:              时间戳
            sign:           加密串
            appid:
            item_id:
            item_price:
            item_count:
            reserved:       扩展参数，SDK发起支付时有传递，则这里会回传。
    """
    if not params:
        params = {
            'trade_no': req.get_argument('trade_no', ''),
            'serialNumber': req.get_argument('serialNumber', ''),
            'money': req.get_argument('money', ''),
            'status': req.get_argument('status', '0'),
            't': req.get_argument('t', ''),
            'sign': req.get_argument('sign', ''),
            'appid': req.get_argument('appid', ''),
            'item_id': req.get_argument('item_id', ''),
            'item_price': req.get_argument('item_price', ''),
            'item_count': req.get_argument('item_count', ''),
            'reserved': req.get_argument('reserved', ''),
        }

    # 支付失败, 按接受成功处理
    if int(params['status']) != 1:
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    sign = params['sign']
    new_sign1 = '%s%s%s%s%s' % (params['serialNumber'], params['money'], params['status'], params['t'], SERVER_KEY)
    new_sign = utils.hashlib_md5_sign(new_sign1)

    if new_sign != sign:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['serialNumber'],   # 自定义定单id
        'order_id': params['trade_no'],           # 平台定单id
        'order_money': float(params['money']),    # 平台实际支付money 单位元
        'uin': '',                                # 平台用户id
        'platform': PLATFORM_NAME,                # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    print login_verify('', {'user_id': '32608510', 'session_id': 'F9A0F6A0E0D4564F56C483165A607735FA4F324'})
    # params = {
    #         'trade_no': 'uy',
    #         'serialNumber': 'q',
    #         'money': '13',
    #         'status': '2',
    #         't': 'aew',
    #         'sign': 'bef3a277c84c8349cd3f17632018f829',
    #         'appid': 'sefe',
    #         'item_id': 'sdefe',
    #         'item_price': 'ewqq',
    #         'item_count': 'efff',
    #         'reserved': 'vxfgd',
    #     }
    # print payment_verify('', params)
