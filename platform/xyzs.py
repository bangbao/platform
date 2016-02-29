# coding: utf-8

import json
import urllib
from helper import http
from helper import utils

__VERSION__ = 'v1.3.1'
PLATFORM_NAME = 'xyzs'
APP_ID = '11111111111'
APP_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
PAY_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
GET_USERINFO_URI = 'http://passport.xyzs.com/checkLogin.php'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'success',
    1: 'fail',
}


def login_verify(req, params=None):
    """用户会话验证
    Args:
        sessionid: sessionid
    Returns:
        用户标识ID
    """
    if not params:
        params = {
            'session_id': req.get_argument('session_id', ''),
            'user_id': req.get_argument('user_id', ''),
            'nickname': req.get_argument('nickname', ''),
        }
    token = params['session_id']
    user_id = params['user_id']
    nickname = params['nickname']

    post_data = urllib.urlencode({
        'uid': user_id,
        'appid': APP_ID,
        'token': token,
    })
    try:
        http_code, content = http.post(GET_USERINFO_URI, post_data, timeout=1)
    except:
        # 平台timeout的概率比较大
        return {'openid': user_id, 'openname': nickname}

    #print http_code, content
    if http_code != 200:
        return None

    #{"ret": 0,"error":'msg'}
    result = json.loads(content)
    if int(result['ret']) != 0:
        return None

    return {
        'openid': user_id,           # 平台标识
        'openname': nickname,        # 平台昵称
    }


def payment_verify(req, params=None):
    """支付回调验证
    Args:
        request包含的参数如下:
            orderid:  xyzs平台订单号
            uid:      xyzs平台用户ID
            serverid: 透传参数。服务器ID,不分服,为0。也可以传其它值
            amount:   人民币消耗金额,单位:元  浮点型
            extra:    透传参数。不要传特殊字符,或 url转义、需编码的字符,128字节内
            ts:       当前时间戳
            sign:     签名
            sig:      签名 2
        params: 测试数据
    """
    if not params:
        params = {
            'orderid': req.get_argument('orderid', ''),
            'uid': req.get_argument('uid', ''),
            'serverid': req.get_argument('serverid', ''),
            'amount': req.get_argument('amount', ''),
            'extra': req.get_argument('extra', ''),
            'ts': req.get_argument('ts', ''),
            'sign': req.get_argument('sign', ''),
            'sig': req.get_argument('sig', ''),
        }

    exclude = ('sign', 'sig')
    sign_items = sorted([(key, value) for key, value in params.iteritems() if key not in exclude])
    query_str = '&'.join('%s=%s' % (key, value) for key, value in sign_items)

    if params['sig']:
        sig_str = '%s%s' % (PAY_KEY, query_str)
        new_sig = utils.hashlib_md5_sign(sig_str)
        if new_sig != params['sig']:
            return RETURN_DATA, None

    sign_str = '%s%s' % (APP_KEY, query_str)
    new_sign = utils.hashlib_md5_sign(sign_str)
    if new_sign != params['sign']:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['extra'],           # 自定义定单id
        'order_id': params['orderid'],             # 平台定单id
        'order_money': float(params['amount']),    # 平台实际支付money 单位元
        'uin': params['uid'],                      # 平台用户id
        'platform': PLATFORM_NAME,                 # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    params = {'user_id': '123123', 'session_id': '85d40ac3d3f8c82946d10d9b2b4c849f', 'nickname': 'nickname'}
    print login_verify('', params)

