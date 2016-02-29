# coding: utf-8

import json
import hmac
import urllib
import hashlib
from helper import http

__VERSION__ = '1.9.4'
PLATFORM_NAME = 'youku'
APP_ID = '1111'
APP_KEY = 'xxxxxxxxxxxx'
APP_SECRET = 'xxxxxxxxxxxxxxxxxxxxx'
PAYMENT_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
# 用SessionID获取用户信息URL
GET_USERINFO_URI = 'http://sdk.api.gamex.mobile.youku.com/game/user/infomation'
try:   # 自己的支付回调地址, 配置在settings文件里
    import settings
    CALLBACK_URL = settings.PAYMENT_NOTIFY_URLS[PLATFORM_NAME]
except:
    CALLBACK_URL = None
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: {'status':'success', 'desc':'pay success'},
    1: {'status': 'failed','respMsg':'sign error'},
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
            'nickname': req.get_argument('nickname', ''),
        }
    session_id = params['session_id']
    nickname = params['nickname']

    sign_str = 'appkey=%s&sessionid=%s' % (APP_KEY, session_id)

    post_data = urllib.urlencode({
        'sessionid': session_id,
        'appkey': APP_KEY,
        'sign': hmac.new(PAYMENT_KEY, sign_str, hashlib.md5).hexdigest(),
    })
    try:    # 数字签名（sign）错误：返回 http 403
        http_code, content = http.post(GET_USERINFO_URI, post_data)
        # print http_code, content
    except:
        return None

    if http_code != 200:
        return None

    # {"status":"success","uid":51871}
    result = json.loads(content)
    if not result.get('uid'):
        return None

    return {
        'openid': result['uid'],                      # 平台标识
        'openname': nickname or result['uid'],        # 平台昵称
    }


def payment_verify(req, params=None):
    """支付回调验证
    Args:
        request包含的参数如下:
            apporderID:     订单号（最长不超过 64 位）
            uid:            用户 id
            price:          价格(单位为“分”)
            sign:           数字签名
            passthrough:    透传参数(最长 128 位)
            result:         计费结果 0:计费失败 1:计费成功 2:计费部分成功(短代支付独有的参数,其他支付方式没有这个参数
            success_amount: 成功支付金额(短代支付独有的参数,其他支付方式没有这个参数)
        params: 测试数据
    Returns:
        支付数据
    """
    if not params:
        params = {
            'apporderID': req.get_argument('apporderID', ''),
            'uid': req.get_argument('uid', ''),
            'price': req.get_argument('price', '0'),
            'sign': req.get_argument('sign', ''),
            'passthrough': req.get_argument('passthrough', ''),
            'result': req.get_argument('result', ''),
            'success_amount': req.get_argument('success_amount', ''),
        }

    if CALLBACK_URL is None:   # 自己的支付回调地址, 配置在settings文件里
        return_data = dict(RETURN_DATA)
        return_data[1] = dict(RETURN_DATA[1], respMsg='callback_url not in settings')
        return return_data, None

    sign_keys = ('apporderID', 'price', 'uid')
    query_str = '&'.join('%s=%s' % (key, params[key]) for key in sign_keys)
    sign_str = '%s?%s' % (CALLBACK_URL, query_str)
    new_sign = hmac.new(PAYMENT_KEY, sign_str, hashlib.md5).hexdigest()
    if new_sign != params['sign']:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['apporderID'],          # 自定义定单id
        'order_id': params['apporderID'],              # 平台定单id
        'order_money': float(params['price']) / 100,   # 平台实际支付money 单位元
        'uin': params['uid'],                          # 平台用户id
        'platform': PLATFORM_NAME,                     # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    # print login_verify('', {'session_id': '85d40ac3d3f8c82946d10d9b2b4c849f'})

    params = {
            'apporderID': '123131',
            'uid': 'werww',
            'price': 'gfdgdg',
            'sign': 'erewr',
            'passthrough': 'fgdgfdg',
            # 'result': req.get_argument('result', ''),
            'success_amount': 'rewrwrwr',
    }
    print payment_verify('', params)


