# coding: utf-8

import json
import time
import urllib
import hashlib
from helper import http

PLATFORM_NAME = 'jinshan'
GID = '111'
SUPPLIER_ID = '111111111'
SUPPLIER_KEY = 'xxxxxxxxxxxx'
PF_ID = '111'
PF_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
GET_USERINFO_URL = 'http://m.wan.liebao.cn/user/validate_mutk'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: {"code": 1, "msg": "success", "data": {"oid": 'platform_order_id'}},
    1: {"code": -1, "msg": "sign error", "data": {"oid": 'platform_order_id'}},
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
            'client_ip': req.request.headers.get('X-Real-IP'),
        }
    mutk = params['session_id']
    client_ip = params['client_ip']

    query_data = {
        'mutk': mutk,
        'supplier_id': SUPPLIER_ID,
        'time': str(int(time.time())),
        'client_ip': client_ip,
    }
    query_data['sign'] = make_jinshan_sign(query_data)

    url = '%s?%s' % (GET_USERINFO_URL, urllib.urlencode(query_data))
    http_code, content = http.get(url, timeout=5)
    #print content
    if http_code != 200:
        return None

    obj = json.loads(content)
    if obj['code'] != 1:
        return None

    return {
        'openid': obj['data']['uid'],      # 平台标识
        'openname': obj['data']['uid'],    # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            pfid:    由游戏提供商分配的金山平台的 ID
            gid:     游戏 ID
            sid:     区服 ID
            uid:     用户 ID
            oid:     订单号
            payway:  支付方式（除非游戏商要求，一般传 alipay）
            gold:    游戏内金币
            money:   充值金额（人民币,单位：分）
            paytime: 支付时间
            cpparam: 游戏内容提供商提供的参数（经过 url escape 编码最长 150 字符）
            time:    时间戳，单位是秒
            sign:    签名字段（加密校验串
        params: 测试专用
    """
    if not params:
        params = {
            'pfid': req.get_argument('pfid', ''),
            'gid': req.get_argument('gid', ''),
            'sid': req.get_argument('sid', ''),
            'uid': req.get_argument('uid', ''),
            'oid': req.get_argument('oid', ''),
            'payway': req.get_argument('payway', ''),
            'gold': req.get_argument('gold', ''),
            'money': req.get_argument('money', ''),
            'paytime': req.get_argument('paytime', ''),
            'cpparam': req.get_argument('cpparam', ''),
            'time': req.get_argument('time', ''),
            'sign': req.get_argument('sign', ''),
        }
    # 生成此次订单验证的返回数据
    return_data = {}
    for rc, obj in RETURN_DATA.iteritems():
        return_data[rc] = dict(obj, data={'oid': params['oid']}),

    verify_sign = make_jinshan_sign(params)
    if verify_sign != params['sign']:
        return return_data, None

    pay_data = {
        'app_order_id': params['cpparam'],              # 自定义定单id
        'order_id': params['oid'],                      # 平台定单id
        'order_money': float(params['money']) / 100,    # 平台实际支付money 单位元
        'uin': params['uid'],                           # 平台用户id
        'platform': PLATFORM_NAME,                      # 平台标识名
    }
    return return_data, pay_data


def make_jinshan_sign(params):
    """对所有参数签名
    1) 将 QueryString 部分的 name 统一成小写（如果本来就小写就忽略）
    2) 将 value 进行 URL UTF8 encode 编码，然后将 name 按字典升序排序，如果参数为空也需要填写“name=”的部分
    3) 将 密 钥 直 接 拼 到 最 后
    4) 把第 3 步得到的密文进行 MD5 运算
    """
    exclude_keys = ('sign',)
    sorted_items = sorted((k.lower(), urllib.quote(v)) for k, v in params.iteritems() if k not in exclude_keys)
    sign_values = ['%s=%s' % (k, v) for k, v in sorted_items]
    sign_data = '&'.join(sign_values)

    return hashlib.md5(sign_data + PF_KEY).hexdigest()


if __name__ == '__main__':
    print login_verify(123123, 'token', '127.0.0.1')



