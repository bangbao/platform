# coding: utf-8

import re
import json
import urllib
import hashlib
from helper import http
from helper import utils

__VERSION__ = '2.4.6'
PLATFORM_NAME = 'zhengyueandroid'
PRODUCTID = 'xxxxxxxxxx'
SERVERID = 'xxxxxxxx'
CLIENT_ID = 'xxxxxxxxxxxxxxxxx'
CLIENT_SECRET = 'xxxxxxxxxxxxxxxxxxxxx'
SYN_KEY = 'xxxxxxxxxxx'
PROJECTID = 'xxxxxxxx'
GET_USER_URI = 'http://srv.zhengyuetech.com/sdksrv/auth/getUserInfo.lg'
GET_ACCESS_TOKEN_URI = 'http://srv.zhengyuetech.com/sdksrv/auth/getToken.lg'
GRANT_TYPE = 'authorization_code'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'success',
    1: 'fail',
}


def login_verify(req, params=None):
    """登录验证
    Args:
        req: request封装，以下是验证所需参数
            session_id: 32 位字符串
        params: 测试专用
    Returns:
        平台相关信息(openid必须有)
    """
    if not params:
        params = {
            'authorization_code': req.get_argument('session_id', ''),
        }

    access_token = get_access_token(params['authorization_code'])
    if not access_token:
        return None

    userinfo_post_data = urllib.urlencode({
        'access_token': access_token,
        'productId': PRODUCTID,
    })
    http_code, content = http.post(GET_USER_URI, userinfo_post_data)
    #print http_code, content
    if http_code != 200:
        return None

    obj = json.loads(content)
    # {u'username': u'U12638056', u'cmStatus': 0, u'codes': u'0', u'id': 10721935, u'sdkuserid': u'U12638056'}
    if int(obj['codes']) != 0:
        return None

    return {
        'openid': obj['sdkuserid'],
        'openname': obj['username'],
        'access_token': access_token,
        'loginName': obj['username'],
        'sdkUserId': obj['sdkuserid'],
        'sdkId': obj['id'],
    }


def get_access_token(authorization_code):
    """通过code获得token
    Args:
        authorization_code: authorization_code
    """
    token_post_data = urllib.urlencode({
        'productId': PRODUCTID,
        'redirect_uri': '1',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': GRANT_TYPE,
        'code': authorization_code,
    })
    http_code, content = http.post(GET_ACCESS_TOKEN_URI, token_post_data)
    #print http_code, content
    if http_code != 200:
        return None

    token_data = json.loads(content)

    return token_data.get('access_token')


def cmge_encode(src, syn_key):
    """用syn_key加密src数据
    """
    rs = []
    data = bytearray(src)
    keys = bytearray(syn_key)
    for idx, i in enumerate(data):
        n = (0xff & i) + (0xff & keys[idx % len(keys)])
        rs.append('@%s' % n)
    return ''.join(rs)


def cmge_decode(src, syn_key):
    """用syn_key解密src数据
    """
    if not src:
        return src

    keys = bytearray(syn_key)
    pattern = re.compile('\\d+')
    l = [int(x) for x in pattern.findall(src)]
    if not l:
        return src

    data = []
    for idx, i in enumerate(l):
        data.append(chr(i - (0xff & keys[idx % len(keys)])))
    return ''.join(data)


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            sign: 签名
            nt_data 解密出的结果
                '<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                    <cmge_message>
                        <message>
                            <login_name>zzzzzzzzcgu</login_name>
                            <game_role>h1buemf-h1-9-1396861797</game_role>
                            <order_id>303222UO10000047588</order_id>
                            <pay_time>2014-04-07 17:05:27</pay_time>
                            <amount>0.01</amount>
                            <status>0</status>
                        </message>
                    </cmge_message>'
        params: 测试专用
    """
    if not params:
        params = {
            'sign': req.get_argument('sign', ''),
            'nt_data': req.get_argument('nt_data', ''),
        }

    conf = {'syn_key': SYN_KEY}

    raw_sign = cmge_decode(params['sign'], conf['syn_key'])
    new_sign = hashlib.md5('nt_data=%s' % params['nt_data']).hexdigest()
    new_sign = list(new_sign)
    trans_template = [(1, 13), (5, 17), (7, 23)]
    for start, end in trans_template:
        new_sign[start], new_sign[end] = new_sign[end], new_sign[start]
    new_sign = ''.join(new_sign)

    if raw_sign != new_sign:
        return RETURN_DATA, None

    order_info = cmge_decode(params['nt_data'], conf['syn_key'])
    params = utils.xml2dict(order_info)

    # 状态为失败按成功返回
    if int(params['status']) != 0:
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    pay_data = {
        'app_order_id': params['game_role'],      # 自定义定单id
        'order_id': params['order_id'],           # 平台定单id
        'order_money': float(params['amount']),   # 平台实际支付money 单位元
        'uin': params['login_name'],              # 平台用户id
        'platform': PLATFORM_NAME,                # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    print login_verify('', {'authorization_code': '304d66bb-fbfd-3ec8-a0fb-313e3bb0e7e4'})




