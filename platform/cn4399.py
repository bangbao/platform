# encoding: utf-8

import json
import urllib
from helper import http
from helper import utils

__VERSION__ = 'v2.3.0.4'
PLATFORM_NAME = '4399'
# GAME_ID = '100133'
# APP_KEY = '102714'
APP_KEY = '111111'
APP_SECRET = 'xxxxxxxxxxxxxxxxxxxxx'
PAY_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxx'
GET_USERINFO_URL = 'http://m.4399api.com/openapi/oauth-check.html'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: {'status': 2, 'code': None, 'money': '1', 'game_money': '10', 'msg': 'ok'},
    1: {'status': 1, 'code': 'other_error', 'money': '1', 'game_money': '10', 'msg': 'fail'},
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
    state = params['session_id']
    uid = params['user_id']
    nickname = params['nickname'] or uid

    sign_str = '%s%s%s%s' % (APP_KEY, uid, state, APP_SECRET)
    query_data = urllib.urlencode({
        'uid': uid,
        'state': state,
        'key': APP_KEY,
        'sign': utils.hashlib_md5_sign(sign_str),
    })
    url = '%s?%s' % (GET_USERINFO_URL, query_data)
    http_code, content = http.get(url)
    # print http_code, content
    if http_code != 200:
        return None

    obj = json.loads(content)
    if int(obj['code']) != 100:
        return None

    return {
        'openid': uid,               # 平台标识
        'openname': nickname,        # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            orderid:  4399 生成的订单号) 22 位以内的字符串 唯一
            p_type:   充值渠道 id
            uid:      要充值的用户 ID,my 平台的用户 uid
            money:    充值金额人民币,单位:元
            gamemoney:兑换的游戏币数量，整数
            serverid: 要充值的服务区号。只针对有分服的游戏有效, 整形
            mark:     订单号:最大长度 32 位,支持大小写字母、数字、‘|’(竖线)、‘-’(中划线)、‘_’(下划线)
            roleid:   要充值的游戏角色 id
            time:     发起请求时的时间戳
            sign:     加密签名,签名计算为:`$sign` =md5(`$orderid` . `$uid` . `$money` .`$gamemoney` . `$serverid` . `$secrect` .
                        `$mark` . `$roleid`.`$time`); 当参数
                        `$serverid`,`$mark` ,`$roleid`为空时,不参与签名计算
        params: 测试专用
    """
    if not params:
        params = {
            'orderid': req.get_argument('orderid', ''),
            'p_type': req.get_argument('p_type', ''),
            'uid': req.get_argument('uid', ''),
            'money': req.get_argument('money', ''),
            'gamemoney': req.get_argument('gamemoney', ''),
            'serverid': req.get_argument('serverid', ''),
            'mark': req.get_argument('mark', ''),
            'roleid': req.get_argument('roleid', ''),
            'time': req.get_argument('time', ''),
            'sign': req.get_argument('sign', ''),
        }
    params['secrect'] = PAY_SECRET

    # 生成返回数据
    return_data = {}
    for code, obj in RETURN_DATA.iteritems():
        return_data[code] = dict(obj, money=params['money'], gamemoney=params['gamemoney'])

    sign_str = ('%(orderid)s%(uid)s%(money)s%(gamemoney)s%(serverid)s'
                '%(secrect)s%(mark)s%(roleid)s%(time)s') % params

    new_sign = utils.hashlib_md5_sign(sign_str)
    if new_sign != params["sign"]:
        return_data[1]['code'] = 'sign_error'
        return return_data, None

    pay_data = {
        'app_order_id': params['mark'],           # 自定义定单id
        'order_id': params['orderid'],            # 平台定单id
        'order_money': float(params['money']),    # 平台实际支付money 单位元
        'uin': params['uid'],                     # 平台用户id
        'platform': PLATFORM_NAME,                # 平台标识名
    }
    return return_data, pay_data


if __name__ == '__main__':
    params = {'session_id': 'b3066822e277f30638966f3e23719de2', 'user_id': '123'}
    print login_verify('', params)


