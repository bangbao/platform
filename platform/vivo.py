# coding: utf-8

import json
import time
import urllib
import hashlib
from helper import http

__VERSION__ = '3.0.1'
PLATFORM_NAME = 'vivo'
APP_ID = 'xxxxxxxxxxxxxxxxxxxxxxx'
CP_ID = 'xxxxxxxxxxxxxxxxx'
CP_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
APP_SECRET_MD5 = hashlib.md5(CP_KEY).hexdigest()
GET_USERINFO_URI = 'https://usrsys.inner.bbk.com/auth/user/info'
# 商户将用户选择的商品信息，推送给vivo支付服务器
GET_VIVOORDER_URI = 'https://pay.vivo.com.cn/vcoin/trade'
# 订单查询接口
QUERY_VIVOORDER_URI = 'https://pay.vivo.com.cn/vcoin/query'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: {"respCode":200,"respMsg":"success"},
    1: {"respCode":400,"respMsg":"failure"},
}


def login_verify(req, params=None):
    """用户会话验证
    Args:
        access_token: access_token
        openid: openid
    Returns:
        用户标识ID
    """
    if not params:
        params = {
            'session_id': req.get_argument('session_id', ''),
            'user_id': req.get_argument('user_id', ''),
            'nickname': req.get_argument('nickname', ''),
        }

    access_token = params['session_id']
    query_data = urllib.urlencode({
        'access_token': access_token,
    })
    http_code, content = http.post(GET_USERINFO_URI, query_data, timeout=2)
    #print http_code, content
    if http_code != 200:
        return None

    obj = json.loads(content)
    if int(obj.get('stat', 200)) != 200:
        return None

    return {
        'openid': obj['uid'],                           # 平台标识
        'openname': obj['nickname'] or obj['uid'],      # 平台昵称
    }


def payment_verify(req, params=None):
    """支付回调验证
    Args:
        params: 字典参数数据
            respCode:      响应码  200
            respMsg:       响应信息说明
            signMethod:    签名方法  对关键信息进行签名的算法名称：MD5
            signature:     签名信息  对关键信息签名后得到的字符串1，用于商户验签
            tradeType:     交易类型  目前固定为1
            tradeStatus:   交易状态  0000 代表支付成功
            cpId:          Cp-id  定长20位数字，由vivo分发的唯一识别码
            appId:         appId  应用ID
            uid:           uid  用户在vivo这边的唯一标识
            cpOrderNumber: 商户自定义的订单号  商户自定义，最长 64 位字母、数字和下划线组成
            orderNumber:   交易流水号  vivo订单号
            orderAmount:   交易金额  单位：分，币种：人民币，为长整型，如：101，10000
            extInfo:       商户透传参数
            payTime:       交易时间  yyyyMMddHHmmss
    """
    if not params:
        params = {
            'respCode': req.get_argument('respCode', ''),
            'respMsg': req.get_argument('respMsg', ''),
            'signMethod': req.get_argument('signMethod', ''),
            'signature': req.get_argument('signature', ''),
            'tradeType': req.get_argument('tradeType', ''),
            'tradeStatus': req.get_argument('tradeStatus', ''),
            'cpId': req.get_argument('cpId', ''),
            'appId': req.get_argument('appId', ''),
            'uid': req.get_argument('uid', ''),
            'cpOrderNumber': req.get_argument('cpOrderNumber', ''),
            'orderNumber': req.get_argument('orderNumber', ''),
            'orderAmount': req.get_argument('orderAmount', ''),
            'extInfo': req.get_argument('extInfo', ''),
            'payTime': req.get_argument('payTime', ''),
        }

    # 交易失败按接受成功处理
    if params['tradeStatus'] != '0000':
        return_data = dict(RETURN_DATA)
        return_data[1] = return_data[0]
        return return_data, None

    new_sign = create_vivo_sign(params)

    if new_sign != params['signature']:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['cpOrderNumber'],                # 自定义定单id
        'order_id': params['orderNumber'],                      # 平台定单id
        'order_money': float(params['orderAmount']) / 100,      # 平台实际支付money 单位元
        'uin': params['uid'],                                   # 平台用户id
        'platform': PLATFORM_NAME,                              # 平台标识名
    }
    return RETURN_DATA, pay_data


def create_vivo_sign(params):
    """生成md5签名
    Args:
        params: 要签名的参数名
    Returns:
        md5签名
    """
    exclude_keys = ('signMethod', 'signature')
    sign_keys = sorted((k for k, v in params.iteritems() if v and k not in exclude_keys))
    sign_values = []
    for k in sign_keys:
        v = params[k]
        if isinstance(v, unicode):
            v = v.encode('utf-8')
        sign_values.append('%s=%s' % (k, v))
    sign_values.append(APP_SECRET_MD5)
    sign_data = '&'.join(sign_values)

    return hashlib.md5(sign_data).hexdigest()


def get_vivo_order(params):
    """获取vivo此次的订单数据
    Args:
        params: 字典参数数据
            version:       接口版本号  方便接口升级，当前为：1.0.0
            signMethod:    签名方法  签名算法，固定值为：MD5
            signature:     签名信息  对关键信息签名后得到的字符串
            cpId:          Cp-id  定长20位数字，在开发者平台注册获取
            appId:         App ID  应用ID，在开发者平台创建应用之后获取
            cpOrderNumber: 商户自定义的订单号  商户自定义，最长 64 位字母、数字和下划线组成,商户订单号必须唯一
            notifyUrl:     异步通知url   交易结束时用于通知商户服务器的url，
            orderTime:     交易开始日期时间  yyyyMMddHHmmss, 交易发生时的时间日期
            orderAmount:   交易金额  单位：分，币种：人民币，必须是整数
            orderTitle:    商品的标题  羽毛球拍
            orderDesc:     订单描述  正品纳米科技台湾产
            extInfo:       CP透传参数  CP扩展参数，异步通知时会透传给CP服务器，最大128位
    Returns:
        订单数据: json格式
            respCode: 成功返回：200，非200时，respMsg会提示错误信息。 当respCode=200时，下列参数有效
            respMsg: 对应响应码的响应信息
            signMethod: 对关键信息进行签名的算法名称：MD5
            signature: 对关键信息签名后得到的字符串1，用于商户验签，
            accessKey: vivoSDK需要的参数
            orderNumber: vivo订单号
            orderAmount: 单位：分，币种：人民币，必须是整数
    """
    post_data = {
        'version': '1.0.0',
        'signMethod': 'MD5',
        'cpId': CP_ID,
        'appId': APP_ID,
        'cpOrderNumber': str(params['cpOrderNumber']),
        'notifyUrl': params['notifyUrl'],
        'orderTime': time.strftime('%Y%m%d%H%M%S'),
        'orderAmount': int(params['orderAmount']),
        'orderTitle': params['orderTitle'].encode('utf-8'),
        'orderDesc': params['orderDesc'].encode('utf-8'),
        'extInfo': str(params['cpOrderNumber']),
    }
    post_data['signature'] = create_vivo_sign(post_data)

    try:
        _, content = http.post(GET_VIVOORDER_URI, urllib.urlencode(post_data), timeout=2)
    except:
        return {}

    return json.loads(content)


def query_vivo_order(params):
    """订单查询接口
    Args:
        params: 字典参数数据
            version:       接口版本号  方便接口升级，当前为：1.0.0
            signMethod:    签名方法  对关键信息进行签名的算法名称：MD5
            signature:     签名信息  对关键信息签名后得到的字符串
            cpId:          Cp-id  定长20位数字，由vivo分发的唯一识别码
            cpOrderNumber: 商户自定义的订单号  商户自定义，最长64位字母、数字和下划线组成，必须唯一
            orderNumber:   交易流水号  vivo订单号
            orderAmount:   交易金额  单位：分，币种：人民币，必须是整数
    return:
        订单情况: json格式
            respCode: 成功返回：200，非200时，respMsg会提示错误信息。 当respCode=200时，下列参数有效
            respMsg: 对应响应码的响应信息
            signMethod: 对关键信息进行签名的算法名称：MD5
            signature: 对关键信息签名后得到的字符串1，用于商户验签，
            tradeType: 交易种类   目前固定01
            tradeStatus: 0000，代表支付成功
            cpId: Cp-id
            appId: 应用ID
            uid: 用户在vivo这边的唯一标识
            cpOrderNumber: 商户自定义，最长 64 位字母、数字和下划线组成
            orderNumber: vivo订单号
            orderAmount: 交易金额 单位：分，币种：人民币，为长整型，如：101，10000
            extInfo: 商户透传参数
            payTime: 交易时间 yyyyMMddHHmmss
    """
    post_data = {
        'version': '1.0.0',
        'signMethod': 'MD5',
        'cpId': CP_ID,
        'cpOrderNumber': str(params['cpOrderNumber']),
        'orderNumber': str(params['orderNumber']),
        'orderAmount': int(params['orderAmount']),
    }
    post_data['signature'] = create_vivo_sign(post_data)

    try:
        _, content = http.post(QUERY_VIVOORDER_URI, urllib.urlencode(post_data), timeout=2)
    except:
        return {}

    return json.loads(content)


if __name__ == '__main__':
    print login_verify('ZjFkZWEwNTdhYzgxOWIyNzU5MDAuMTg1MDI5ODUuMTM5ODIzOTY3ODg3NA%3D%3D')
    params = dict([
                    ("cpOrderNumber", "h17048734-h1-1-1398260680"),
                    ("notifyUrl", "http://dev.kaiqigu.net/genesis/pay/?method=callback&tp=vivo"),
                    ("orderTime", "20140423222934"),
                    ("orderAmount", "6.00"),
                    ("orderTitle", u'60 6\u94bb\u77f3\u5305'),
                    ("orderDesc", u'60 6\u94bb\u77f3\u5305'),
                ])
    print get_vivo_order(params)
    params = dict([
                    ("cpOrderNumber", "h17048734-h1-1-1398260680"),
                    ("orderAmount", "6.00"),
                    ("orderNumber", '139830413404229548476'),
                ])
    print query_vivo_order(params)


