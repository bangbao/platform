# coding: utf-8

import json
import urllib
from helper import http
from helper import utils

PLATFORM_NAME = 'kuaiwan'
APP_KEY = 'xxxxxx'
VERIFY_LOGIN_URL = 'http://user.dyn.mobi.kuaiwan.com/account/session/check/'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: {'result':'1'},
    1: {'result':'-2'},
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
    sid = params['session_id']

    query_str = urllib.urlencode({
        'sid': sid,
    })

    url = '%s?%s' % (VERIFY_LOGIN_URL, query_str)
    http_code, content = http.get(url, timeout=5)

    if http_code != 200:
        return None

    obj = json.loads(content)
    openid = obj['data']['user_id']          # 平台用户ID
    return {
        'openid': openid,          # 平台用户ID
        'openname': openid,      # 平台用户名字
    }

def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            user_id:         快玩玩家通行证
            order_no:        快玩订单号
            ext_order_num:   游戏厂商订单号
            ext_product_id:  游戏厂商产品
            money:           充值RMB
            token:           认证串
        params: 测试专用
    """
    if not params:
        params = {
            'user_id': req.get_argument('user_id', ''),
            'order_no': req.get_argument('order_no', ''),
            'ext_order_num': int(req.get_argument('ext_order_num', 0)),
            'ext_product_id': req.get_argument('ext_product_id', ''),
            'money': req.get_argument('money', ''),
            'token': req.get_argument('token', ''),
        }
    params['key'] = APP_KEY

    sign_str = '%s%s%s%s' % (params['user_id'], params['money'], params['order_no'], params['key'])
    new_sign = utils.hashlib_md5_sign(sign_str)
    if new_sign != params['token']:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['ext_order_num'],         # 自定义定单id
        'order_id': params['order_no'],                  # 平台定单id
        'order_money': float(params['money']),           # 平台实际支付money 单位元
        'uin': params['user_id'],                        # 平台用户id
        'platform': PLATFORM_NAME,                       # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    print login_verify('540683828226441ab111194b2d2e3d0f')
    #params = {'user_id':'242964320','money':'1','order_no':'GP140903181559832144','token':'8c707850b10cf11142614482463440a6'}
    #print payment_verify(params)
