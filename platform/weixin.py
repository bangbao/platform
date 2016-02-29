# encoding: utf-8

import time
import json
import urllib
import hashlib
import hmac
import binascii
from helper import http
from helper import utils


# 无真正的参数
__VERSION__ = 'v2.3.9d'
PLATFORM_NAME = 'weixin'
APP_ID = 'xxxxxxxxxxxx'
APP_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
PAY_SECRET = '%s&' % APP_KEY
APP_USERINFO_URL = 'http://msdktest.qq.com/auth/check_token/'
# 正式环境支付扣费验证地址
WX_VERIFY_RECEIPTS_URL = 'http://msdk.qq.com/mpay/buy_goods_m'
# 沙箱环境支付扣费验证地址
WX_SANDBOX_VERIFY_RECEIPTS_URL = 'http://msdktest.qq.com/mpay/buy_goods_m'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: {"ret": 0, "msg": "ok"},
    1: {"ret": 4, "msg": "请求参数错误：（sig）"},
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

    openid = params['user_id']
    accessToken = params['session_id']
    timestamp = int(time.time())

    sign_str = '%s%s' % (APP_KEY, timestamp)
    sig = utils.hashlib_md5_sign(sign_str)
    query_data = urllib.urlencode({
        'timestamp': timestamp,
        'appid': APP_ID,
        'sig': sig,
        'openid': openid,
        'encode': 1,
    })
    url = '%s?%s' % (APP_USERINFO_URL, query_data)

    post_data1 = {
        'openid': openid,
        'openkey': accessToken,
    }
    post_data = json.dumps(post_data1)

    http_code, content = http.post(url, post_data)
    print http_code, content
    if http_code != 200:
        return None

    # {"ret":0,"msg":"ok"}
    # 0成功
    obj = json.loads(content)
    if int(obj['ret']) != 0:
        return None

    return {
        'openid': openid,          # 平台标识
        'openname': openid,        # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            openid:               从手Q登录态中获取的openid的值。由平台直接传给应用，应用原样传给平台即可
            appid:                应用的唯一ID。可以通过appid查找APP基本信息。
            ts:                   linux时间戳。秒为单位 注意开发者的机器时间与腾讯计费开放平台的时间相差不能超过15分钟
            payitem:              物品信息 （1）接收标准格式为ID*price*num，回传时ID为必传项。批量购买套餐物品则用“;”分隔，字符串中不能包含"|"特殊字符。
                                          （2）ID表示物品ID，price表示单价（以Q点为单位，单价最少不能少于1Q点，1Q币=10Q点。单价的制定需遵循道具定价规范），num表示最终的购买数量。
            token:                应用调用mpay/buy_goods_m接口成功返回的交易token。交易token的有效期为15分钟
            billno:               支付流水号（64个字符长度。该字段和openid合起来是唯一的）。
            version:              协议版本号，由于基于V3版OpenAPI，这里一定返回“v3”。
            zoneid:               在分区配置里的分区ID即为这里的“zoneid”。如果应用不分区，移动端的zoneid则默认为1。回调发货的时候，根据这里填写的zoneid实现分区发货
            providetype:          发货类型。5表示移动端道具购买
            amt:                  Q点/Q币消耗金额或财付通游戏子账户的扣款金额。可以为空，若传递空值或不传本参数则表示未使用Q点/Q币/财付通游戏子账户。以0.1Q点为单位
            payamt_coins:         扣取的游戏币总数，单位为Q点
            pubacct_payamt_coins: 扣取的抵用券总金额，单位为Q点
            appmeta:              在buy_goods_m的设定的自定义参数app_metadata，会透传到appmeta里
            clientver:            客户端渠道。Android平台的应用回调时返回clientver=android，IOS平台的应用返回时clientver=iap。
            sig:                  请求串的签名
        params: 测试专用
    """
    if not params:
        params = {
            'openid': req.get_argument('openid', ''),
            'ts': req.get_argument('ts', ''),
            'payitem': req.get_argument('payitem', ''),
            'token': req.get_argument('token', ''),
            'billno': req.get_argument('billno', ''),
            'version': req.get_argument('version', ''),
            'zoneid': req.get_argument('zoneid', ''),
            'providetype': req.get_argument('providetype', ''),
            'amt': req.get_argument('amt', ''),
            'payamt_coins': req.get_argument('payamt_coins', ''),
            'pubacct_payamt_coins': req.get_argument('pubacct_payamt_coins', ''),
            'appmeta': req.get_argument('appmeta', ''),
            'clientver': req.get_argument('clientver', ''),
            'sig': req.get_argument('sig', ''),
        }
    params['appid'] = APP_ID

    # 生成返回数据
    return_data = {}
    for code, obj in RETURN_DATA.iteritems():
        return_data[code] = dict(obj)

    method = 'GET'
    url_path = '/mpay/buy_goods_m'
    exclude_keys = ('sign',)
    params1 = {}
    str1 = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!*()'
    for k, v in params.iteritems():
        if k not in exclude_keys:
            for x in v:
                if x not in str1:
                    v = v.replace(x, '%s%s' % ('%', binascii.hexlify(x).upper()))
            params1[k] = v

    new_sign = hmac_sha1_sig(method, url_path, params1, PAY_SECRET)
    if new_sign != params['sign']:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['appmeta'],          # 自定义定单id
        'order_id': params['billno'],               # 平台定单id
        'order_money': float(params['amt']) / 100,  # 平台实际支付money 单位元
        'uin': params['openid'],                    # 平台用户id
        'platform': PLATFORM_NAME,                  # 平台标识名
    }
    return return_data, pay_data


def get_wx_order(params, sandbox=False):
    method = 'GET'
    url_path = '/mpay/buy_goods_m'

    sig = hmac_sha1_sig(method, url_path, params, APP_KEY)
    params['sig'] = sig

    if sandbox:
        url = '%s%s?%s' % (WX_SANDBOX_VERIFY_RECEIPTS_URL, url_path, urllib.urlencode(params))
    else:
        url = '%s%s?%s' % (WX_VERIFY_RECEIPTS_URL, url_path, urllib.urlencode(params))

    cookies = urllib.urlencode({
        'session_id': 'openid',
        'session_type': 'kp_actoken',
        'org_loc': url_path,
    })
    headers = {"Cookie": cookies}

    rc, data = http.get(url, headers=headers, timeout=2)

    data = json.loads(data)
    if rc != 200:
        return False, data

    if data['ret'] != 0:
        return False, data
    return True, data


def hmac_sha1_sig(method, url_path, params, secret):
    source = mk_soucrce(method, url_path, params)
    hashed = hmac.new(secret, source, hashlib.sha1)
    return binascii.b2a_base64(hashed.digest())[:-1]


def mk_soucrce(method, url_path, params):
    str_params = urllib.quote_plus("&".join(k + "=" + str(params[k]) for k in sorted(params.keys())), '')
    source = '%s&%s&%s' % (
        method.upper(),
        urllib.quote_plus(url_path, ''),
        str_params
    )
    return source


if __name__ == '__main__':
    params = {'session_id': 'b3066822e277f30638966f3e23719de2', 'user_id': 'weyiqu'}
    print login_verify('wew', params)


