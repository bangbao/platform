# coding: utf-8

import copy
import time
import urllib
from helper import http
from helper import utils

__VERSION__ = 'v2.1.4'
# 平台名字
PLATFORM_NAME = 'hupu'
GAME_ID = 102
#PAY_SERVERID = 322
# 线上线下公用参数
APP_ID = 11111
APP_KEY = 'xxxxxxxxxxxxxxxxxxx'
PAY_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
GET_USER_URI = 'http://youxi.hupu.com/ioauth/verify'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: {'code': 0, 'roleid': ''},
    1: {'code': 1, 'roleid': ''},
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
    session_id = params['session_id']
    user_id = params['user_id']
    nickname = params['nickname'] or user_id

    query_data = {
        'appid': APP_ID,
        'uid': user_id,
        'gameid': GAME_ID,
        'token': session_id,
        'timeline': int(time.time()),
        'method': 'POST',
    }
    sign_str = urllib.urlencode(sorted(query_data.iteritems()))
    query_data['sign'] = utils.hmac_sha1_sign(APP_KEY, sign_str)
    # 对方验证只是走个形式．．．阿弥陀佛
    headers = {'User-Agent': 'PythonServer'}
    http_code, content = http.post(GET_USER_URI, urllib.urlencode(query_data),
                                   headers=headers)
    #print http_code, repr(content)
    if http_code != 200:
        return None

    # 返回１代表成功，其它失败
    # 返回值竟然不是'1', 而是'\xef\xbb\xbf1', 好诡异
    if int(content[-1]) != 1:
        return None

    return {
        'openid': user_id,         # 平台用户ID
        'openname': nickname,      # 平台用户名字
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            partnerid:   联营商 ID
            gameid:      游戏 ID (开发方提供)
            serverid:    服务器 ID (开发方提供)
            userid:      账号(虎扑提供的唯一用户识别,开发方需要记录日志 )
            eventtime:   时间，过期时间为 60 [yyyyMMddHHmmss] time
            orderid:     虎扑生成的联营商订单号 string
            rmb:         虎扑玩家支付的人民币金额，单位：元 int
            sign:        签名MD5 校验码， 参数的 MD5 签名
            transparent: 透传参数，自定义
        params: 测试专用
    """
    if not params:
        params = {
            'partnerid': req.get_argument('partnerid', ''),
            'gameid': req.get_argument('gameid', ''),
            'serverid': req.get_argument('serverid', 0),
            'userid': req.get_argument('userid', ''),
            'eventtime': req.get_argument('eventtime', ''),
            'orderid': req.get_argument('orderid', ''),
            'rmb': req.get_argument('rmb', 0),
            'sign': req.get_argument('sign', ''),
            'transparent': req.get_argument('transparent', ''),
        }
    params['key'] = PAY_KEY
    return_data = copy.deepcopy(RETURN_DATA)
    return_data[0]['roleid'] = params['userid']
    return_data[1]['roleid'] = params['userid']

    sign_str = ('%(partnerid)s'
                '%(gameid)s'
                '%(serverid)s'
                '%(userid)s'
                '%(eventtime)s'
                '%(orderid)s'
                '%(rmb)s'
                '%(transparent)s'
                '%(key)s') % params
    new_sign = utils.hashlib_md5_sign(sign_str)
    if params['sign'] != new_sign:
        return return_data, None

    pay_data = {
        'app_order_id': params['transparent'],         # 自定义定单id
        'order_id': params['orderid'],                 # 平台定单id
        'order_money': float(params['rmb']),           # 平台实际支付money 单位元
        'uin': params['userid'],                       # 平台用户id
        'platform': PLATFORM_NAME,                     # 平台标识名
    }
    return return_data, pay_data


if __name__ == '__main__':
    params = {'session_id': '34684388a97f284e264dc548e7d2582626834f840311c9ca',
              'user_id': '123123', 'nickname': 'nickname'}
    print login_verify('', params=params)


