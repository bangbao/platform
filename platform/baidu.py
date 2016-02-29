# coding: utf-8

import json
import base64
import urllib
from helper import http
from helper import utils

__VERSION__ = 'v3.0.0'
PLATFORM_NAME = 'baidu'
APP_ID = '111111'
APP_KEY = 'xxxxxxxxxxxxxxx'
SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
VERIFY_SESSIONID_URI = 'http://querysdkapi.91.com/CpLoginStateQuery.ashx'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: {'AppID': APP_ID, 'ResultCode': 1, 'ResultMsg':'success', 'Sign': '', 'Content': ''},
    1: {'AppID': APP_ID, 'ResultCode': 0, 'ResultMsg':'failure', 'Sign': '', 'Content': ''},
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
    AccessToken = params['session_id']
    nickname = params['nickname']

    sign_str = "%s%s%s" % (APP_ID, AccessToken, SECRET_KEY)
    sign = utils.hashlib_md5_sign(sign_str)

    query_data = urllib.urlencode({
        'AppID': APP_ID,
        'AccessToken': AccessToken,
        'Sign': sign,
    })
    http_code, content = http.post(VERIFY_SESSIONID_URI, query_data)
    #print http_code, content
    if http_code != 200:
        return None

    result = json.loads(content)
    if int(result['ResultCode']) != 1:
        return None

    Content = base64.b64decode(result['Content'])
    obj = json.loads(Content)

    return {
        'openid': obj['UID'],                     # 平台标识
        'openname': nickname or obj['UID'],       # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            AppID:                 应用 ID，对应游戏客户端中使用的 APPID
            OrderSerial:           SDK 系统内部订单号
            CooperatorOrderSerial: CP 订单号
            Sign:                  签名
            Content:  JSON 编码格式:UTF-8,Base64 编码
                UID:             用户 ID
                MerchandiseName: 商品名称
                OrderMoney:      订单金额,保留两位小数。单位:元
                StartDateTime:   订单创建时间 格式:yyyy-MM-dd HH:mm:ss
                BankDateTime:    银行到帐时间 格式:yyyy-MM-dd HH:mm:ss
                OrderStatus:     支付状态：0=失败，1=成功
                StatusMsg:       StatusMsg
                ExtInfo:         ExtInfo
        params: 测试专用
    """
    if not params:
        params = {
            'AppID': req.get_argument('AppID', ''),
            'OrderSerial': req.get_argument('OrderSerial', ''),
            'CooperatorOrderSerial': req.get_argument('CooperatorOrderSerial', ''),
            'Sign': req.get_argument('Sign', ''),
            'Content': req.get_argument('Content', ''),
        }
    params['SecretKey'] = SECRET_KEY

    # 生成返回数据
    return_data = {}
    for code, data in RETURN_DATA.iteritems():
        ResultCode = 1 if code == 0 else 0
        return_Sign = utils.hashlib_md5_sign('%s%s%s' % (APP_ID, ResultCode, SECRET_KEY))
        return_data[code] = dict(data, AppID=params['AppID'], Sign=return_Sign)

    sign_str = ('%(AppID)s'
                '%(OrderSerial)s'
                '%(CooperatorOrderSerial)s'
                '%(Content)s'
                '%(SecretKey)s') % params
    new_sign = utils.hashlib_md5_sign(sign_str)
    if new_sign != params['Sign']:
        return return_data, None

    content = base64.b64decode(params['Content'])
    obj = json.loads(content)
    # 支付状态：0=失败，1=成功
    if int(obj['OrderStatus']) != 1:
        return_data[1] = return_data[0]
        return return_data, None

    pay_data = {
        'app_order_id': params['CooperatorOrderSerial'],     # 自定义定单id
        'order_id': params['OrderSerial'],                   # 平台定单id
        'order_money': float(obj['OrderMoney']),             # 平台实际支付money 单位元
        'uin': obj['UID'],                                   # 平台用户id
        'platform': PLATFORM_NAME,                           # 平台标识名
    }
    return RETURN_DATA, pay_data


# def query_order(params):
#     """
#     Args:
#         params:
#             AppID:                     Int Y 应用 ID
#             CooperatorOrderSerial:     String Y CP 订单号
#             OrderType:                 Int Y 固定值:1
#             Sign:                      String Y 签名
#             Action:                    Int Y 固定值:10002
#     """
#     QUERY_URL = 'http://querysdkapi.91.com/CpOrderQuery.ashx'
#
#     sign_str = "%s%s%s" % (APP_ID, params['CooperatorOrderSerial'], SECRET_KEY)
#     sign = utils.hashlib_md5_sign(sign_str)
#
#     query_data = urllib.urlencode({
#         'AppID': APP_ID,
#         'CooperatorOrderSerial': params['CooperatorOrderSerial'],
#         'OrderType': 1,
#         'Sign': sign,
#         'Action': 10002,
#     })
#     http_code, content = http.post(QUERY_URL, query_data)
#     print http_code, content



if __name__ == '__main__':
    params = {'session_id': '1312312', 'nickname': 'nickname'}
    print login_verify('', params)


