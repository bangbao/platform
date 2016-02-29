# encoding: utf-8

import re
import json
import urllib
import hashlib
from helper import http
from helper import utils

__VERSION__ = 'v1.1'
PLATFORM_NAME = 'zhuoyue'  # 中手游 卓越越狱版
PRODUCT_ID = 'xxxxxxxx'
SERVER_ID = 'xxxxxxx'
PROJECT_ID = 'xxxxxxxx'
SYN_KEY = 'xxxxxxxxxxxxxxxxxxx'
APP_KEY = 'xxxxxxxxxxxxxxx'
APP_SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxx'
APP_USERINFO_URL = 'http://yx.sdksrv.com/sdksrv/auth/getUserInfo.lg'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'success',
    1: 'failed',
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
    access_token = params['session_id']
    user_id = params['user_id']

    post_data = {
        'access_token': access_token,
        'productId': PRODUCT_ID,
        '__e__': '1',
    }

    params_keys = sorted(((k, v) for k, v in post_data.iteritems() if v))
    sign_values = ('%s=%s' % (k, v) for k, v in params_keys)
    sign_data1 = '&'.join(sign_values)
    sign_data = '%s&%s' % (sign_data1, APP_KEY)
    sign0 = utils.hashlib_md5_sign(sign_data)
    sign1 = list(sign0)
    trans_template = [(1, 13), (5, 17), (7, 23)]
    for start, end in trans_template:
        sign1[start], sign1[end] = sign1[end], sign1[start]
    sign = ''.join(sign1)
    post_data['sign'] = sign

    query_data = urllib.urlencode(post_data)
    http_code, content = http.post(APP_USERINFO_URL, query_data)
    #print http_code, content
    if http_code != 200:
        return None

    # {"id":11226132,"codes":"0","cmStatus":null,"username":"U18553987A","sdkuserid":"U18553987A"}
    # 0成功, 1失败
    obj = json.loads(content)
    if int(obj['codes']) != 0:
        return None

    return {
        'openid': obj['sdkuserid'],         # 平台标识
        'openname': obj['username'],        # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            sign: 签名
            nt_data 解密出的结果
                '<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                    <cmge_message>
                        <message>
                            <login_name>zzzzzzzzcgu</login_name>             用户登录名
                            <game_role>h1buemf-h1-9-1396861797</game_role>   CP自定义信息
                            <order_id>303222UO10000047588</order_id>         SDK订单号
                            <pay_time>2014-04-07 17:05:27</pay_time>         交易时间
                            <amount>0.01</amount>                            成交金额，单位元
                            <status>0</status>                               交易状态，0表示成功
                        </message>
                    </cmge_message>'
        params: 测试专用
    """
    if not params:
        params = {
            'sign': req.get_argument('sign', ''),
            'nt_data': req.get_argument('nt_data', ''),
        }
    syn_dict = {'syn_key': SYN_KEY}

    raw_sign = cmge_decode(params['sign'], syn_dict['syn_key'])
    new_sign = hashlib.md5('nt_data=%s' % params['nt_data']).hexdigest()
    new_sign = list(new_sign)
    trans_template = [(1, 13), (5, 17), (7, 23)]
    for start, end in trans_template:
        new_sign[start], new_sign[end] = new_sign[end], new_sign[start]
    new_sign = ''.join(new_sign)

    if raw_sign != new_sign:
        return RETURN_DATA, None

    order_info = cmge_decode(params['nt_data'], syn_dict['syn_key'])
    params = utils.xml2dict(order_info)
    # print locals()
    # 状态为失败按成功返回
    if int(params['status']) != 0:
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    pay_data = {
        'app_order_id': params['game_role'],      # 自定义定单id
        'order_id': params['order_id'],           # 平台定单id
        'order_money': float(params['amount']),   # 平台实际支付money 单位元
        'uin': '',                                # 平台用户id
        'platform': PLATFORM_NAME,                # 平台标识名
    }
    return RETURN_DATA, pay_data


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


if __name__ == '__main__':
    params = {'session_id': '91a', 'user_id': '062'}
    print login_verify('', params)
    sign = '@216@113@159@221@158@101@160@150@155@219@214@146@157@173@156@161@200@166@171@175@175@110@200@224@157@99@211@151@205@173@217@103'
    nt_data = '@178@119@222@231@217@80@227@199@221@233@222@159@167@183@138@157@147@166@155@154@219@166@201@233@209@153@219@201@168@152@202@132@127@167@160@142@133@233@237@219@228@156@199@230@220@158@210@159@141@228@228@82@120@184@164@207@210@221@222@217@227@157@217@237@206@151@210@160@167@227@218@163@172@219@207@209@163@178@229@233@221@161@212@217@219@145@218@199@169@218@217@150@161@226@210@207@203@220@224@182@165@164@213@225@214@158@204@208@204@227@218@110@117@225@201@217@202@213@235@233@226@157@164@220@157@97@206@195@228@175@170@96@102@170@153@153@154@163@170@174@168@113@157@178@162@104@159@155@167@165@220@145@166@223@199@222@212@226@222@184@178@167@216@222@210@162@204@203@207@180@168@97@114@170@156@162@157@203@200@171@166@104@150@170@159@99@166@148@158@171@182@108@104@233@218@208@202@232@216@227@218@118@162@234@206@169@204@214@212@227@218@110@107@170@153@161@146@166@173@167@168@107@134@171@165@106@161@151@165@170@169@108@104@234@201@229@196@234@226@231@219@118@162@219@218@159@226@208@223@180@166@94@105@170@164@155@198@227@232@239@228@172@164@182@224@164@206@214@224@233@179@96@117@169@219@224@198@234@238@237@180@116@149@231@210@163@224@195@210@219@179@108@104@221@213@211@202@213@230@223@233@171@199@225@210@110'
    print payment_verify('', {'sign': sign, 'nt_data': nt_data})
