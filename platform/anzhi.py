# coding: utf-8

import json
import time
import base64
import urllib
from helper import http
from helper import utils

__VERSION__ = '3.2'
PLATFORM_NAME = 'anzhi'
APP_KEY = 'xxxxxxxxxxxxxxx'
APP_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxx'
QUERY_LOGIN_URL = 'http://user.anzhi.com/web/api/sdk/third/1/queryislogin'
#CREATE_BIND_URL = 'http://user.anzhi.com/web/api/sdk/1/user-create-bind'
QUERY_ORDER_URL = 'http://pay.anzhi.com/web/api/third/1/queryorder'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'success',
    1: 'failure',
}


def login_verify(req, params=None):
    """登陆验证
    Args:
        openid: 平台id
        sid: 会话session_id
    Returns:
        平台id
    """
    if not params:
        params = {
            'user_id': req.get_argument('user_id', ''),
            'session_id': req.get_argument('session_id', ''),
            'nickname': req.get_argument('nickname', ''),
        }
    sid = params['session_id']
    open_id = params['user_id']
    nickname = params['nickname']

    data = urllib.urlencode({
        'time': time.strftime('%Y%m%d%H%M%S123'),
        'appkey': APP_KEY,
        'sid': sid,
        'sign': base64.b64encode(APP_KEY+sid+APP_SECRET),
    })
    http_code, content = http.post(QUERY_LOGIN_URL, data, timeout=1)
    #print http_code, content
    if http_code != 200:
        return None

    # 平台返回JSON数据中竟然使用单引号。。。
    if "'" in content:
        content = content.replace("'", '"')

    #{'time':'20130709150615195', 'msg':'eyd1aWQnOicyMDEzMDcwODE4MjgzOWxZdlkyYmJsbmInfQ==',
    # 'sc':'1','st':'成功(sid 有效)'}
    obj = json.loads(content)
    if int(obj['sc']) != 1:
        return None

    msg_data = base64.b64decode(obj['msg'])
    # 平台返回JSON数据中竟然使用单引号。。。
    if "'" in msg_data:
        msg_data = msg_data.replace("'", '"')
    data = json.loads(msg_data)

    return {
        'openid': data['uid'],                            # 平台标识
        'openname': data.get('nickname', nickname),       # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        params: 回调字典数据
            data: 支付加密数据
                uid:          安智账号 id uid 在匿名支付的时候为空
                orderId:      订单号
                orderAmount:  订单金额(单位为分)
                orderTime:    支付时间
                orderAccount: 支付账号
                code:         订单状态 （1 为成功）
                msg:          msg
                payAmount:    实际支付金额(单位为分)
                cpInfo:       回调信息 用户自定义参数
                notifyTeime:  通知时间
                memo:         备注
                redBagMoney:  礼券金额(单位为分)礼券金额是游戏厂商承担,该金额不参与结算分成 。
                                注意：(一)若用户没有使用礼券支付,通知没有该字段。
                                     (二)若用户使用包含礼券支付,金额是礼券金额。
    """
    if not params:
        params = {
            'data': req.get_argument('data', ''),
        }

    try:
        b64data = base64.b64decode(params['data'])
        des_data = utils.des3_decrypt(APP_SECRET, b64data)
    except:
        return RETURN_DATA, None

    data = json.loads(des_data)
    # 不成功时直接返回success
    if int(data['code']) != 1:
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    # # 不在重新请求数据，加快速度
    # sign_str = '%s%s%s' % (APP_KEY, data['orderId'], APP_SECRET)
    # query_data = urllib.urlencode({
    #     'time': time.strftime('%Y%m%d%H%M%S123'),
    #     'appkey': APP_KEY,
    #     'type': 0,
    #     'tradenum': data['orderId'],
    #     'mintradetime': '',
    #     'maxtradetime': '',
    #     'sign': base64.b64encode(sign_str),
    # })
    # http_code, content = http.post(QUERY_ORDER_URL, query_data)
    # #print http_code, content
    # if http_code != 200:
    #     return RETURN_DATA, None
    #
    # # 平台返回JSON数据中竟然使用单引号。。。
    # if "'" in content:
    #     content = content.replace("'", '"')
    #
    # result = json.loads(content)
    # if int(result['sc']) not in (1, 200):
    #     return RETURN_DATA, None
    # 不验证列表中数据了
    #msg_list = base64.b64decode(result['msg'])

    pay_data = {
        'app_order_id': data['cpInfo'],                   # 自定义定单id
        'order_id': data['orderId'],                      # 平台定单id
        'order_money': float(data['payAmount']) / 100,    # 平台实际支付money 单位元
        'uin': data['uid'],                               # 平台用户id
        'platform': PLATFORM_NAME,                        # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    # print login_verify('a', {'session_id': '34684388a97f284e264dc548e7d2582626834f840311c9ca', 'user_id': 'wew', 'nickname': 'adwd'})
    data = 'GVWrnGmnnXB16a7HkoIIFYImI7z7dDAoHry4gfxH8DTsP24LtePbV6QVV09Psq8Y%2F59VIPMpx3GUYZKGBnYf51pR4DO2KYWQ4ewfbN6UQsjaWwQ7%2FvousHp7apzNIPVo%2B1rz3RP8V9zPeaEi3AXmMSNhyJeZIeMZcd%2Bw9t06NEb4FYy%2Benil0204L5FIoR1MSV7ls67iC5YN5R9N8G%2Blo7eqd86VjnukkOyouIOVACCCK5FYYWv9aMFpA9h%2BDgnHaTvSAbgVhee%2FQ0xFCTGveY081ztjaaIJYR9nLXXkR3HB6lrcSBnpC%2BhPbalFwpy1pIvis1gZ3fdpDil5e9TZLIRyTktmq2%2FU'
    data = urllib.unquote(data)
    print payment_verify('', {'data': data})
