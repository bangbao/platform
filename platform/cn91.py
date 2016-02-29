# coding: utf-8

import json
import urllib
from helper import http
from helper import utils

__VERSION__ = '1.02'
PLATFORM_NAME = '91'
APP_ID = '111111'
APP_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
LOGIN_ACT_ID = 4
PAYMENT_ACT_ID = 1
VERIFY_SESSIONID_URI = 'http://service.sj.91.com/usercenter/AP.aspx'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: {'ErrorCode':'1','ErrorDesc':'接收成功'},
    1: {'ErrorCode':'0','ErrorDesc':'接收失败'},
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
            'nickname': req.get_argument('nickname', '')
        }
    session_id = params['session_id']
    uin = params['user_id']
    nickname = params['nickname']

    sign_str = "%s%s%s%s%s" % (APP_ID, LOGIN_ACT_ID, uin, session_id, APP_KEY)
    sign = utils.hashlib_md5_sign(sign_str)

    query_data = urllib.urlencode({
        'AppId': APP_ID,
        'Act': LOGIN_ACT_ID,
        'Uin': uin,
        'SessionId': session_id,
        'Sign': sign,
    })
    url = '%s?%s' % (VERIFY_SESSIONID_URI, query_data)
    try:
        http_code, content = http.get(url)
        # print http_code, content
    except:    # timeout时跳过验证
        return {'openid': uin, 'openname': nickname}

    if http_code != 200:
        return None

    obj = json.loads(content)
    # 错误码(0=失败，1=成功(SessionId 有效)，2= AppId 无效，3= Act无效，4=参数无效，5= Sign 无效，11=SessionId 无效
    if int(obj['ErrorCode']) != 1:
        return None

    return {
        'openid': uin,           # 平台标识
        'openname': nickname,    # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            AppId:           应用 ID，对应游戏客户端中使用的 APPID
            Act:             固定值1
            ProductName:     应用名称
            ConsumeStreamId: 消费流水号
            CooOrderSerial:  商户订单号， 自定义格式
            Uin:             91 账号 ID
            GoodsId:         商品 ID
            GoodsInfo:       商品名称
            GoodsCount:      商品数量
            OriginalMoney:   原始总价(格式：0.00) 单位元
            OrderMoney:      实际总价(格式：0.00)
            Note:            即支付描述（自定义格式）
            PayStatus:       支付状态：0=失败，1=成功
            CreateTime:      创建时间(yyyy-MM-dd HH:mm:ss)
            Sign:            签名,­‐将以上参数加 key 后得到的签名
        params: 测试专用
    """
    if not params:
        params = {
            'AppId': req.get_argument('AppId', ''),
            'Act': req.get_argument('Act', ''),
            'ProductName': req.get_argument('ProductName', ''),
            'ConsumeStreamId': req.get_argument('ConsumeStreamId', ''),
            'CooOrderSerial': req.get_argument('CooOrderSerial', ''),
            'Uin': req.get_argument('Uin', ''),
            'GoodsId': req.get_argument('GoodsId', ''),
            'GoodsInfo': req.get_argument('GoodsInfo', ''),
            'GoodsCount': req.get_argument('GoodsCount', ''),
            'OriginalMoney': req.get_argument('OriginalMoney', ''),
            'OrderMoney': req.get_argument('OrderMoney', ''),
            'Note': req.get_argument('Note', ''),
            'PayStatus': req.get_argument('PayStatus', 0),
            'CreateTime': req.get_argument('CreateTime', ''),
            'Sign': req.get_argument('Sign', ''),
        }
    params['AppKey'] = APP_KEY

    sign_str = ('%(AppId)s'
                '%(Act)s'
                '%(ProductName)s'
                '%(ConsumeStreamId)s'
                '%(CooOrderSerial)s'
                '%(Uin)s'
                '%(GoodsId)s'
                '%(GoodsInfo)s'
                '%(GoodsCount)s'
                '%(OriginalMoney)s'
                '%(OrderMoney)s'
                '%(Note)s'
                '%(PayStatus)s'
                '%(CreateTime)s'
                '%(AppKey)s') % params
    new_sign = utils.hashlib_md5_sign(sign_str)
    if new_sign != params['Sign']:
        return RETURN_DATA, None

    # 支付状态：0=失败，1=成功
    if int(params['PayStatus']) != 1:
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    pay_data = {
        'app_order_id': params['CooOrderSerial'],         # 自定义定单id
        'order_id': params['ConsumeStreamId'],            # 平台定单id
        'order_money': float(params['OriginalMoney']),    # 平台实际支付money 单位元
        'uin': params['Uin'],                             # 平台用户id
        'platform': PLATFORM_NAME,                        # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    print login_verify('', {'session_id': '11111', 'user_id': 'bbbbbb', 'nickname': 'nickname'})

