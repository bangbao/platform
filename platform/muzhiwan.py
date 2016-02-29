# coding: utf-8

import json
import urllib
import hashlib
from helper import http

__VERSION__ = 'v2.1.1'
PLATFORM_NAME = 'muzhiwan'
APP_KEY = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'
PAY_KEY = '111111111111111111111111'
GET_USERINFO_URL = 'http://sdk.muzhiwan.com/oauth2/getuser.php'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'SUCCESS',
    1: 'NOT SUCCESS',
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
        }
    token = params['session_id']

    query_data = urllib.urlencode({
        'token': token,
        'appkey': APP_KEY,
    })
    url = '%s?%s' % (GET_USERINFO_URL, query_data)
    try:
        # 对方服务器不稳定
        http_code, content = http.get(url)
    except:
        return None
    #print http_code, content
    if http_code != 200:
        return None

    # {"code”:”1”,"msg”:””,”user”:{"username”:””,"uid”:””,"sex”:0,"mail”:””,"icon”:””}}
    obj = json.loads(content)
    if int(obj['code']) != 1:
        return None

    return {
        'openid': obj['user']['uid'],               # 平台用户ID
        'openname': obj['user']['username'],        # 平台用户名字
    }



def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            appkey:      游戏唯一标记
            orderID:     订单唯一标记
            productName: 商品名称
            productDesc: 商品描述
            productID:   商品ID
            money:       金额，为整形，无小数点，元为单位
            uid:         充值用户ID
            extern:      扩展域
            sign:        签名
        params: 测试专用
    """
    if not params:
        params = {
            'appkey': req.get_argument('appkey', ''),
            'orderID': req.get_argument('orderID', ''),
            'productName': req.get_argument('productName', ''),
            'productDesc': req.get_argument('productDesc', ''),
            'productID': req.get_argument('productID', ''),
            'money': req.get_argument('money', ''),
            'uid': req.get_argument('uid', ''),
            'extern': req.get_argument('extern', ''),
            'sign': req.get_argument('sign', ''),
        }

    sign_sort_keys = ('appkey', 'orderID', 'productName', 'productDesc', 'productID',
                      'money', 'uid', 'extern')
    sign_values = [params[k].encode('utf-8') if isinstance(params[k], unicode) else params[k]
                   for k in sign_sort_keys]
    sign_values.append(PAY_KEY)
    sign_str = ''.join(sign_values)
    new_sign = hashlib.md5(sign_str).hexdigest()
    if new_sign != params['sign']:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['extern'],          # 自定义定单id
        'order_id': params['orderID'],             # 平台定单id
        'order_money': float(params['money']),     # 平台实际支付money 单位元
        'uin': params['uid'],                      # 平台用户id
        'platform': PLATFORM_NAME,                 # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    print login_verify('34684388a97f284e264dc548e7d2582626834f840311c9ca')

