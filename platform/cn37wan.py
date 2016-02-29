# encoding: utf-8

import time
import json
import urllib
from helper import http
from helper import utils

__VERSION__ = '1.0.0.1'
PLATFORM_NAME = '37wan'
PARTNER_ID = '1'    # 联运商 ID
GAME_ID = '111111'
APP_KEY = 'zzzzzzzzzzzzzzzz&czJWiaL/'
PAY_KEY = 'zzzzzzzzzzzzzzzzzzzz;2ASkhOoF4U*t'
APP_USERINFO_URL = 'http://vt.api.m.37.com/verify/token/'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: {"state": 1, "data": None, "msg": "success"},
    1: {"state": 0, "data": None, "msg": "failure"},
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
    token = params['session_id']

    timestamp = int(time.time())
    sign_str = '%s%s%s' % (GAME_ID, timestamp, APP_KEY)
    sign = utils.hashlib_md5_sign(sign_str)

    query_data = urllib.urlencode({
        'pid': PARTNER_ID,
        'gid': GAME_ID,
        'time': timestamp,
        'sign': sign,
        'token': token,
    })
    http_code, content = http.post(APP_USERINFO_URL, query_data)
    # print http_code, content
    if http_code != 200:
        return None

    # {"state":0,"data":[],"msg":"签名错误"}
    # 1成功, 0失败
    obj = json.loads(content)
    # print obj['msg']
    if int(obj['state']) != 1:
        return None

    return {
        'openid': obj['data']['uid'],              # 平台标识
        'openname': obj['data']['disname'],        # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            #pid: Int 联运商
            #gid: Int 游戏 ID
            time: Int Unix 时间戳 √
            sign: String 校验令牌 (md5("{$time}{$key}{$oid}{$doid}{$dsid}{$uid}{$money}{$coin}")) √
            oid: String 联运平台订单 ID √
            doid: String CP 订单 ID   √
            dsid: Int CP 游戏服 ID   √
            #dext: String CP 扩展回调参数
            #drid: Int CP 角色 ID
            #drname: String CP 角色名
            #drlevel Int CP 角色等级
            uid Int 用户 UID √
            money: float 金额 √
            coin: Int 游戏币 √
            #remark: String 简单的备注
            #paid: String 平台应用标识
        params: 测试专用
    """
    if not params:
        params = {
            'time': req.get_argument('time', ''),
            'sign': req.get_argument('sign', ''),
            'oid': req.get_argument('oid', ''),
            'doid': req.get_argument('doid', ''),
            'dsid': req.get_argument('dsid', ''),
            'uid': req.get_argument('uid', ''),
            'money': req.get_argument('money', ''),
            'coin': req.get_argument('coin', ''),
        }
    params['pay_key'] = PAY_KEY

    sign_str = ('%(time)s'
                '%(pay_key)s'
                '%(oid)s'
                '%(doid)s'
                '%(dsid)s'
                '%(uid)s'
                '%(money)s'
                '%(coin)s') % params
    new_sign = utils.hashlib_md5_sign(sign_str)
    if new_sign != params['sign']:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['doid'],           # 自定义定单id
        'order_id': params['oid'],                # 平台定单id
        'order_money': float(params['money']),    # 平台实际支付money 单位元
        'uin': params['uid'],                     # 平台用户id
        'platform': PLATFORM_NAME,                # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    params = {'session_id': 'b3066822e277f30638966f3e23719de2'}
    print login_verify('', params)


