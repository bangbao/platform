# encoding: utf-8

import time
import json
import urllib
import hashlib
import hmac
import binascii
from helper import http
from helper import utils

# 无真正参数
__VERSION__ = 'v3.0'
PLATFORM_NAME = 'tencent'
APP_ID = '123456'
APP_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx '
SECRET_KEY = '%s&' % APP_KEY
PF = 'qzone'
URI = '/v3/user/get_info'
# 正式环境下URL
APP_USERINFO_URL = 'http://openapi.tencentyun.com/v3/user/get_info'
# # 测试环境下URL
# APP_USERINFO_URL = 'http://119.147.19.43/v3/user/get_info'
# 正式环境支付扣费验证地址
VERIFY_RECEIPTS_URL = 'https://openapi.tencentyun.com/mpay/buy_goods_m'
# 沙箱环境支付扣费验证地址
SANDBOX_VERIFY_RECEIPTS_URL = 'http://119.147.19.43/mpay/buy_goods_m'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: {"ret": 0, "msg": "ok"},
    1: {"ret": 4, "msg": "请求参数错误：（sig）"} ,
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
            'nickname': req.get_argument('nickname', ''),
        }

    openid = params['user_id']
    openkey = params['session_id']
    method = 'GET'
    url_path = URI
    post_data = {'openid': openid, 'openkey': openkey, 'appid': APP_ID, 'pf': PF}
    sig = hmac_sha1_sig(method, url_path, post_data, SECRET_KEY)

    query_data = urllib.urlencode({
        'openid': openid,
        'openkey': openkey,
        'appid': APP_ID,
        'sig': sig,
        'pf': PF,
    })
    url = '%s?%s' % (APP_USERINFO_URL, query_data)
    http_code, content = http.get(url)
    print http_code, content
    if http_code != 200:
        return None

    # {"ret":0,"msg":"user is logged in"}
    # 0成功
    obj = json.loads(content)
    if int(obj['ret']) != 0:
        return None

    return {
        'openid': openid,                   # 平台标识
        'openname': params['nickname'],     # 平台昵称
    }


def payment_verify(params, sandbox=False):
    """支付回调验证
    """
    method = 'GET'
    url_path = '/mpay/pay_m'

    sig = hmac_sha1_sig(method, url_path, params, APP_KEY)
    params['sig'] = sig

    if sandbox:
        url = '%s%s?%s' % (SANDBOX_VERIFY_RECEIPTS_URL, url_path, urllib.urlencode(params))
    else:
        url = '%s%s?%s' % (VERIFY_RECEIPTS_URL, url_path, urllib.urlencode(params))

    cookies = ';'.join(['session_id=openid', 'session_type=kp_actoken', 'org_loc=%s' % url_path])
    headers = {'Cookie': cookies}
    rc, data = http.get(url, headers=headers)

    data = json.loads(data)
    if rc != 200:
        return False, data

    if data['ret'] != 0:
        return False, data
    return True, data


def get_qq_order(params, sandbox=False):
    """购买道具下订单
    Args:
        openid:         从手Q登录态中获取的openid的值
        openkey:        从手Q登录态中获取的access_token 的值
        pay_token:      从手Q登录态中获取的pay_token的值
        appid:          应用的唯一ID
        ts:             UNIX时间戳
        payitem:        请使用x*p*num的格式，x表示物品ID，p表示单价,num表示默认的购买数量
        goodsmeta:      物品信息，格式必须是“name*des”
        goodsurl:       物品的图片url(长度<512字符)。
        sig:            请求串的签名
        pf:             平台来源
        zoneid:         账户分区ID_角色
        pfkey:          登录成功后平台直接传给应用，应用原样传给平台即可强校验
        amt:            (可选)道具总价格。（amt必须等于所有物品：单价*建议数量的总和,该参数的单位为0.1Q点，即1分钱）。
        max_num :       (可选) 用户可购买的道具数量的最大值。
        appmode:        (可选)1表示用户不可以修改物品数量，
        app_metadata :  （可选）发货时透传给应用，长度必须<=128字符。
        userip:         （可选）用户的外网IP。
        format:         （可选）json、jsonp_$func。默认json。如果jsonp
    """
    method = 'GET'
    url_path = '/mpay/buy_goods_m'

    sig = hmac_sha1_sig(method, url_path, params, APP_KEY)
    params['sig'] = sig
    if sandbox:
        url = '%s%s?%s' % (SANDBOX_VERIFY_RECEIPTS_URL, url_path, urllib.urlencode(params))
    else:
        url = '%s%s?%s' % (VERIFY_RECEIPTS_URL, url_path, urllib.urlencode(params))

    cookies = ';'.join(['session_id=openid', 'session_type=kp_actoken', 'org_loc=%s' % url_path])
    headers = {'Cookie': cookies}
    rc, data = http.get(url, headers=headers)

    data = json.loads(data)
    return data['ret'], data


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
    params = {'session_id': 'b3066822e277f30638966f3e23719de2', 'user_id': 'weyiqu', 'nickname': 'weixin'}
    print login_verify('wew', params)
    # params = {
    #     'openid': 'F11669C63D76BAB0BC2F6CC869B19E53',
    #     'openkey': '3968DD5F3F14427EF103A05E00AB59B4',
    #     'pf': 'desktop_m_qq-10000144-android-2002-',
    #     'pfkey': 'd0cd576ad99fcea674f09ce24da65345',
    #     'pay_token': '91E5CE357A0EE02C9C105FBF95703001',
    #     'ts': 1396324143,
    #     'payitem': 'G1*20*2',
    #     'goodsmeta': 'name*goodsinfo',
    #     'goodsurl': 'http://imgcache.qq.com/qzone/space_item/pre/0/66768.gif',
    #     'zoneid': 1,
    #     'app_metadata': 'customkey',
    #     'format': 'json',
    #     'appid': 1101255891,
    # }
    # print get_qq_order(params)

