# coding: utf-8

import urllib
from helper import http
from helper import utils

__VERSION__ = 'v2.0'  # 登录版本号
PLATFORM_NAME = 'tongbu'
APP_ID = '111111'
APP_KEY = 'zzzzz#xxxxxxxxxxxxx#xxx'
CHECKKV_TOKEN_URL = 'http://tgi.tongbu.com/api/LoginCheck.ashx'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: {'status': 'success'},
    1: {'status': 'error'},
}


def login_verify(req, params=None):
    """sid用户会话验证
    Args:
        session_id: 用户会话ID
        user_id: 用户平台ID, 即与session_id对应的用户标识id
    Returns:
        用户标识id
    """
    if not params:
        params = {
            'session_id': req.get_argument('session_id', ''),
            'user_id': req.get_argument('user_id', ''),
        }
    session = params['session_id']
    user_id = params['user_id']

    query_data = urllib.urlencode({
        'session': session,
        'appid': APP_ID,
    })
    url = '%s?%s' % (CHECKKV_TOKEN_URL, query_data)
    try:
        http_code, content = http.get(url)
        # print http_code, content
    except:
        # tongbu服务器经常性timeout, 所以发生错误就直接跳过验证
        return {'openid': user_id, 'openname': user_id}

    if http_code != 200:
        return None

    open_id = int(content)
    # 0表示失效， -1表示格式有错
    if open_id in (0, -1):
        return None

    return {
        'openid': open_id,          # 平台标识
        'openname': open_id,        # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        params: 验证需要的所有数据,以下是必须的
            source:   数据来源，默认值 tongbu
            trade_no: 订单编号，自定义格式
            amount:   金额，单位为分
            partner:  游戏编号-­‐-­‐-­‐-­‐同步游戏联运平台为游戏分配的唯一编号
            paydes:   支付说明
            debug:    是否调试模式(判断订单是否是测试订单)
            tborder:  同步订单号（3.1 新增）
            sign:     签名,­‐将以上参数加 key 后得到的签名
    """
    if not params:
        params = {
            'source': req.get_argument('source', ''),
            'trade_no': req.get_argument('trade_no', ''),
            'amount': int(req.get_argument('amount', 0)),
            'partner': req.get_argument('partner', ''),
            'paydes': req.get_argument('paydes', ''),
            'debug': req.get_argument('debug', ''),
            'tborder': req.get_argument('tborder', ''),
            'sign': req.get_argument('sign', ''),
        }
    params['key'] = APP_KEY

    sign_str = ('source=%(source)s&'
                'trade_no=%(trade_no)s&'
                'amount=%(amount)s&'
                'partner=%(partner)s&'
                'paydes=%(paydes)s&'
                'debug=%(debug)s&'
                'tborder=%(tborder)s&'
                'key=%(key)s') % params
    new_sign = utils.hashlib_md5_sign(sign_str)
    if new_sign != params['sign']:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['trade_no'],             # 自定义定单id
        'order_id': params['tborder'],                  # 平台定单id
        'order_money': float(params['amount']) / 100,   # 平台实际支付money 单位元
        'uin': '',                                      # 平台用户id
        'platform': PLATFORM_NAME,                      # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    print login_verify('', {'session_id': 'tSQl4OfSJ', 'user_id': '123'})

