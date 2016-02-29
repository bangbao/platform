# encoding: utf-8

import json
import urllib
import hashlib
from helper import http

__VERSION__ = '4.0.1'
PLATFORM_NAME = 'downjoy'
MERCHANT_ID = '11111'
APP_ID = '1111'
APP_KEY = 'xxxxx'
PAYMENT_KEY = 'xxxxxxxxxxxxx'
APP_USERINFO_URL = 'http://ngsdk.d.cn/api/cp/checkToken'
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
    mid = params['user_id']

    sign_str = '|'.join([APP_ID, APP_KEY, token, mid])
    sig = hashlib.md5(sign_str).hexdigest()

    query_data = urllib.urlencode({
        'appid': APP_ID,
        'umid': mid,
        'token': token,
        'sig': sig,
    })
    url = '%s?%s' % (APP_USERINFO_URL, query_data)
    http_code, content = http.get(url)
    #print http_code, content
    if http_code != 200:
        return None

    data = json.loads(content)
    if data['msg_code'] != 2000:
        return None
    if int(data['valid']) != 1:
        return None

    return {
        'openid': mid,                     # 平台标识
        'openname': params['nickname'],    # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            result:    支付结果,固定值。 1代表成功, 0代表失败
            money:     支付金额,单位:元,两位小数。
            order:     本次支付的订单号。
            mid:       本次支付用户的乐号,既登录后返回的 mid 参数。
            time:      时间戳,格式:yyyymmddHH24mmss 月日小时分秒小于 10 前面补充 0
            signature: MD5 验证串,用于与接口生成的验证串做比较,保证计费通知的合法性。
            ext:       客户端购买商品时候传入的 TransNo 字段 。(厂家用于金额验证)
        params: 测试专用
    """
    if not params:
        params = {
            'result': req.get_argument('result', ''),
            'money': req.get_argument('money', ''),
            'order': req.get_argument('order', ''),
            'mid': req.get_argument('mid', ''),
            'time': req.get_argument('time', ''),
            'signature': req.get_argument('signature', ''),
            'ext': req.get_argument('ext', ''),
        }

    if int(params['result']) != 1:
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    params['key'] = PAYMENT_KEY

    pre_sign = ('order=%(order)s&'
                'money=%(money)s&'
                'mid=%(mid)s&'
                'time=%(time)s&'
                'result=%(result)s&'
                'ext=%(ext)s&'
                'key=%(key)s') % params
    new_sign = hashlib.md5(pre_sign).hexdigest()
    if new_sign != params["signature"]:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['ext'],            # 自定义定单id
        'order_id': params['order'],              # 平台定单id
        'order_money': float(params['money']),    # 平台实际支付money 单位元
        'uin': params['mid'],                     # 平台用户id
        'platform': PLATFORM_NAME,                # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    print login_verify('', {'user_id': '32608510', 'session_id': 'F9A0F6A0E0D4564F56C483165A607735FA4F324'})

