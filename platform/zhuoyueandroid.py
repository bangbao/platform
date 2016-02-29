# encoding: utf-8

import re
import json
import urllib
import hashlib
from helper import http
from helper import utils

__VERSION__ = 'v1.1'
PLATFORM_NAME = 'zhuoyueandroid'  # 中手游 卓越android版
PRODUCT_ID = 'xxxxxx'
SERVER_ID = 'xxxxxxxxx'
PROJECT_ID = 'xxxxx'
SYN_KEY = 'xxxxxxxxxxxxxxxxxx'
APP_KEY = 'xxxxxxxxxxxxxxxxxxx'
APP_SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxx'
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
    # sign = '@167@213@192@196@164@151@152@197@156@151@173@197@168@161@214@166@149@198@211@204@157@147@162@157@172@194@168@210@166@212@152@153'
    # nt_data = '@162@181@219@223@222@83@236@221@232@222@208@160@162@113@146@100@149@96@90@153@203@228@198@225@214@156@228@223@179@141@188@133@122@97@168@85@135@163@172@218@212@218@196@222@225@161@219@181@152@217@214@83@115@114@172@150@212@151@157@216@211@219@214@229@211@154@219@182@178@216@204@164@167@149@215@152@165@108@164@232@205@223@209@209@224@148@227@221@180@226@207@150@101@102@163@111@150@156@167@224@207@228@194@224@211@160@219@182@178@210@200@158@153@147@226@162@211@149@118@235@213@226@200@174@161@154@215@229@219@202@217@160@160@153@174@111@214@162@156@222@216@213@204@214@176@100@193@199@167@155@151@97@100@100@160@99@151@96@105@181@149@229@213@214@215@165@213@225@218@169@163@161@149@173@207@167@208@157@157@183@152@166@148@165@159@99@171@165@166@157@135@98@108@110@161@100@161@101@111@181@149@230@196@235@209@167@223@229@219@169@163@146@161@163@229@161@219@110@109@169@148@166@147@174@161@148@227@231@235@217@219@111@112@167@228@148@219@165@171@183@150@178@146@229@230@148@234@237@233@169@163@96@161@153@227@166@200@151@157@183@162@165@198@223@217@152@213@229@219@222@218@146@155@153@174'
    # print payment_verify('', {'sign': sign, 'nt_data': nt_data})
