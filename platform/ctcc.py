# coding: utf-8

import json
import urllib
import time
from helper import http
from helper import utils

# 电信平台
__VERSION__ = '2.0.2'
PLATFORM_NAME = 'ctcc'
GAME_ID = '1111111'
APP_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxx'
CLIENT_ID = '1111111'
CLIENT_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
# # demo参数
# CLIENT_ID = '84106431'
# CLIENT_SECRET = '8b16b0ec91934e25b8d60d36ef52f4c8'
GET_USERINFO_URL = 'https://open.play.cn/oauth/token'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: '<cp_notify_resp><h_ret>0</h_ret><cp_order_id>%(cp_order_id)s</cp_order_id></cp_notify_resp>',
    1: '<cp_notify_resp><h_ret>1</h_ret><cp_order_id>%(cp_order_id)s</cp_order_id></cp_notify_resp>',
}


def login_verify(req, params=None):
    """登录验证
    """
    if not params:
        params = {
            'session_id': req.get_argument('session_id'),
        }
    code = params['session_id']
    sign_sort = 'client_id&sign_method&version&timestamp&client_secret'

    post_data = {
        'client_id': CLIENT_ID,
        'sign_method': 'MD5',
        'version': '1.0',
        'timestamp': int(time.time()),
        'sign_sort': sign_sort,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
    }
    signature = '%(client_id)s%(sign_method)s%(version)s%(timestamp)s%(client_secret)s' % post_data
    post_data['signature'] = utils.hashlib_md5_sign(signature)

    query_data = urllib.urlencode(post_data)
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    http_code, content = http.post(GET_USERINFO_URL, query_data, headers=headers)
    #print http_code, content
    if http_code != 200:
        return None

    # {"scope": "all","re_expires_in": 15552000,"user_id": 956877,"token_type": "Bearer",
    #  "expires_in": 5184000,"refresh_token": "2c639e8c1cbfeee5fb07e968163d0343",
    #  "access_token": "2cd0a6f9c8ce81ada335f1989413ca08"}
    obj = json.loads(content)
    if obj.get('error'):
        return None

    return {
        'openid': obj['user_id'],                    # 平台标识
        'openname': obj['user_id'],                  # 平台昵称
        'access_token': obj['access_token'],         # 访问令牌
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            cp_order_id:  CP业务流水号
            correlator:   爱游戏平台流水号
            result_code:  00为扣费成功，其他状态码均为扣费不成功请勿发放道具
            fee:          计费金额，单位：元
            pay_type:     计费类型，smsPay：短代；alipay：支付宝；ipay：爱贝
            method:       固定值“callback”
            sign:         MD5(cp_order_id+correlator+result_code+fee+paytype+method+appKey)
            version:      回调接口版本号，当前为1。
        params: 测试专用
    """
    if not params:
        params = {
            'cp_order_id': req.get_argument('cp_order_id', ''),
            'correlator': req.get_argument('correlator', ''),
            'result_code': req.get_argument('result_code', ''),
            'fee': req.get_argument('fee', 0),
            'pay_type': req.get_argument('pay_type', ''),
            'method': req.get_argument('method', ''),
            'sign': req.get_argument('sign', ''),
            'version': req.get_argument('version', ''),
        }
    params['appKey'] = APP_KEY

    # 生成返回数据
    return_data = {}
    for code, msg_string in RETURN_DATA.iteritems():
        return_data[code] = msg_string % params

    # 扣费不成功时按接受成功处理
    if params['result_code'] != '00':
        return_data[1] = return_data[0]
        return return_data, None

    sign_str = ('%(cp_order_id)s'
                '%(correlator)s'
                '%(result_code)s'
                '%(fee)s'
                '%(pay_type)s'
                '%(method)s'
                '%(appKey)s') % params
    new_sign = utils.hashlib_md5_sign(sign_str)
    if new_sign != params['sign']:
        return return_data, None

    pay_data = {
        'app_order_id': params['cp_order_id'],      # 自定义定单id
        'order_id': params['correlator'],           # 平台定单id
        'order_money': float(params['fee']),        # 平台实际支付money 单位元
        'uin': '',                                  # 平台用户id
        'platform': PLATFORM_NAME,                  # 平台标识名
    }
    return return_data, pay_data


if __name__ == '__main__':
    params = {'session_id': '98d158a557b88f5a0725dd4692cc7dac'}
    print login_verify('', params)
    params = {
            'cp_order_id': 'asd',
            'correlator': 'sad',
            'result_code': '00',
            'fee': 234,
            'pay_type': 'smsPay',
            'order_time': '1212122132',
            'method': 'callback',
            'sign': 'e8071e63ddf56b9e6510c0f94e7b9e93',
            'version': '1',
        }
    #print payment_verify('', params)

