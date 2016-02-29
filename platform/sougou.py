# coding: utf-8

import json
import urllib
import hashlib
from helper import http

__VERSION__ = 'v.14_27_landscape'
PLATFORM_NAME = 'sougou'
GID = '479'
# APP_ID = '479'
APP_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
APP_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
PAY_KEY = '{xxxxxx-F715-xxxxxxx-A74C-xxxxxxxxxxxx}'
#DEV_LOGIN_VERIFY = 'http://dev.app.wan.sogou.com/api/v1/login/verify'
PRD_LOGIN_VERIFY = 'http://api.app.wan.sogou.com/api/v1/login/verify'
# OK    成功/重复成功订单
# ERR_100    参数不符合规则
# ERR_200    验证失败
# ERR_300    账号不存在
# ERR_400    非法IP访问
# ERR_500    其他错误
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'OK',
    1: 'ERR_200',
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
    session_key = params['session_id']
    user_id = params['user_id']

    post_data = {
        'gid': GID,
        'session_key': session_key,
        'user_id': user_id,
    }
    post_data['auth'] = generate_sougou_sign(post_data, APP_SECRET)

    query_str = urllib.urlencode(post_data)
    http_code, content = http.post(PRD_LOGIN_VERIFY, query_str, timeout=1)
    # print http_code, content
    if http_code != 200:
        return None

    obj = json.loads(content)
    if not obj.get('result'):
        return None

    return {
        'openid': user_id,          # 平台用户ID
        'openname': user_id,        # 平台用户名字
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            gid:        game id 由平台分配的游戏编号
            sid:        server id 由平台分配的游戏区服编号
            uid:        user id 平台的用户id
            role:       若游戏需充值到角色，传角色名。默认会传空
            oid:        订单号，同一订单有可能多次发送通知
            date:       订单创建日期，格式为yyMMdd
            amount1:    用户充值金额（人民币元）
            amount2:    金额（游戏币数量）
            time:       通知发送的时间
            appdata:    透传参数（可无），若需要须向平台方申请开启此功能，默认开启
            realAmount: 用户充值真实金额（人民币元）
            auth:       验证字符, 附加支付秘钥
        params: 测试专用
    """
    if not params:
        params = {
            'gid': req.get_argument('gid', ''),
            'sid': req.get_argument('sid', ''),
            'uid': req.get_argument('uid', ''),
            'role': req.get_argument('role', ''),
            'oid': req.get_argument('oid', ''),
            'date': req.get_argument('date', ''),
            'amount1': req.get_argument('amount1', ''),
            'amount2': req.get_argument('amount2', ''),
            'time': req.get_argument('time', ''),
            'appdata': req.get_argument('appdata', ''),
            'realAmount': req.get_argument('realAmount', ''),
            'auth': req.get_argument('auth', ''),
        }
    new_sign = generate_sougou_sign(params, PAY_KEY)
    if new_sign != params['auth']:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['appdata'],             # 自定义定单id
        'order_id': params['oid'],                     # 平台定单id
        'order_money': float(params['realAmount']),    # 平台实际支付money 单位元
        'uin': params['uid'],                          # 平台用户id
        'platform': PLATFORM_NAME,                     # 平台标识名
    }
    return RETURN_DATA, pay_data


def generate_sougou_sign(params, sign_key):
    """生成签名
    Args:
        params: 参数字典
        sign_key: 签名用的key
    Returns:
        md5签名
    """
    exclude = ('auth',)
    sorted_items = sorted((k, v) for k, v in params.iteritems() if k not in exclude)
    params_str = urllib.urlencode(sorted_items)
    sign_str = '%s&%s' % (params_str, sign_key)

    return hashlib.md5(sign_str).hexdigest()


if __name__ == '__main__':
    print login_verify('', {'session_id':'34684388a97f284e264dc548e7d2582626834f840311c9ca', 'user_id': '123231'})
    data = {'gid': 62, 'session_key': 'a1e912a708b9f9a669eca53a4b1180822d8fee58e01d63552b0178e3da84b614',
            'user_id': '8411626'}
    # sign = '31474948ac1926d155bc837885d6a296'
    print generate_sougou_sign(data, '862653da5865293b1ec8cc1cab258cbc51acc8')


