# coding: utf-8

import json
import time
import base64
from helper import http
from helper import utils
from helper import oauth

__VERSION__ = 'v2.2.0.a'
PLATFORM_NAME = 'jinli'
APP_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
APP_SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBALNsAWbDBhQ6spxx
HixRJEC7MNTLheqMnAzYB4gJD0dHNaNx+tsZNuBptOQb89loy2VAmi2JV3D3BrGq
JCmFGYMxbGrooi1S6bKzbXxFHBsz/pUCdgWBv6Tb1sDC5/XXf2kUVuYjz6o4OgzE
PCiMk+E/pms9fMd8DFzfi3vEvlW1AgMBAAECgYA23dtb2l2ciAqgjnLkqHeGl/ep
ywcLn64Eu3cqIWMbr+n2Ll/A6mf+njSj4Oxj2okAUI4VSL+FmvTgFaBzVfFjyv31
4EBE3ho0d6CffbXHgXp/xrG+qdzzcBRHnTZa0LVkOMiVsLNHvLY2Myd1RNk0PdCy
f35V5FljM4jALt4TDQJBANkB5w0VWTCjI6IrioDIDn/JHu+xbYMD3iWf6sXSkYeW
+jTq3drMNdsgOOxeMvEUy5a7MMun3fOOazA7V6eqJjsCQQDTqTXsAD0Q5v2dOBgi
m78Mc0U8jqU1S55IQsVC6xw0Ad3ct2eS//LtPcLpywXw8ntqcWM95T65y5oR+oWV
KYTPAkADWCYpa3TObRU1gJpH1c1zZrQVWZSoejzIM6i4l8AqaMc+XYhBwPfrgpmd
+u2qDXn9vrDH0rR29nDsc12sddDVAkBnQGo/gDZJ4oThhxWu/E8MYcbqraNGBmdm
VLwp0stlS2vRWd66xQTaWoCU0CdLzN4LpNiGvygENqAoGQ/FHgXdAkAzWdDdNYQj
UWegzdoOAzLQEC21adFogMfZe2/0GrRdZqzAtG8yy49qhqgoKRo4LMRIP8vnocDn
KB5x8N7LurWP
-----END PRIVATE KEY-----"""
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCXE4C+SBp28Hlviweyr6bUOfWH
ZgEQLxZG2R9P+SLURoMO01kP4tVWAj51wwwXM50YorkWHjucoVWKt513Qus+Tun8
UxDabuaFIoYyhgCDjQxRvu7bQk8wG8VWGVXjKNR0+LieBADp7HribZVhKtRaYLm2
mJK5c/s2pVwMB+TTrwIDAQAB
-----END PUBLIC KEY-----"""
GET_USERINFO_URL = 'https://id.gionee.com/account/verify.do'
HOST = "id.gionee.com"
PORT = "443"
URI = "/account/verify.do"
METHOD = "POST"
CREATE_PAYMENT_ORDER_URL = 'https://pay.gionee.com/order/create'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'success',
    1: 'not success',
}


def login_verify(req, params=None):
    """登陆验证
    Args:
        amigoToken: amigoToken
    Returns:
        用户标识
    """
    if not params:
        params = {
            'user_id': req.get_argument('user_id', ''),
            'nickname': req.get_argument('nickname', ''),
            'session_id': req.get_argument('session_id', ''),
        }
    user_id = params['user_id']
    nickname = params['nickname']
    amigoToken = params['session_id']

    ts = str(oauth.generate_timestamp())
    nonce = oauth.generate_nonce(8).upper()
    sign_str = '\n'.join((ts, nonce, METHOD, URI, HOST, PORT, '\n'))
    sign = utils.hmac_sha1_sign(APP_SECRET_KEY, sign_str, hexdigest=False)
    signature = base64.b64encode(sign)
    authorization = 'MAC id="%s",ts="%s",nonce="%s",mac="%s"' % (APP_KEY, ts, nonce, signature)
    http_code, content = http.post(GET_USERINFO_URL, amigoToken,
                                   headers={'Authorization': authorization,
                                            'Content-Type': 'application/json'},
                                   timeout=2)
    #print http_code, content
    if http_code != 200:
        return None

    # {"r":"1011", "wid":"38c6aa98-b220-49e5-94f5-fab0f8d00838","u":"9FBDC73FC6734B0BBCF9AF208A453F13",
    # "tn":"15311521854","na":"Amigo_你好","ptr":" ","ul":30,"sty":0,
    # "ply":[{"a":"D4D91AA8707C4201B09A108E6156CB14","pid":"877CC9677D8248D1872EC41BCC11B26E","na":"Amigo_21739"}]}
    obj = json.loads(content)
    if obj.get('r', 0) != 0:
        return None

    # 平台未返回ply时使用前端发的
    if 'ply' in obj:
        player = obj['ply'][0]
    elif user_id and nickname:
        player = {'pid': user_id, 'na': nickname}
    else:
        return None

    return {
        'openid': player['pid'],       # 平台标识
        'openname': player['na'],      # 平台昵称
    }


def create_pay_order(params):
    """创建此次的订单数据
    Args:
        params: 字典参数数据
            player_id:    字符串 玩家id（不参与签名）
            api_key:      商户APIKey
            deal_price:   字符串 必填 商品总金额
            deliver_type: 字符串 必填 付款方式：1为立即付款，2为货到付款 (目前支付方式1，请选1)
            expire_time:  字符串 可选 订单过期时间，必须大于订单提交时间 如果有该字段，必须参与签名
            notify_url:   字符串 可选 服务器通知地址，如果有该字段，必须参与签名
            out_order_no: 字符串 必填 商户订单号,由商户自定义,数字、字母或"-"、"_"、"|"构成,64个字符以内复
            subject:      字符串 必填 商品名称，32个字符以内，不能含有半用 “+”、“&”或特殊字符集
            submit_time:  字符串 必填 订单提交时间，格式为 yyyyMMddHHmmss
            total_fee:    字符串 必填 需支付金额， 值必须等 于商品总 金额 23 （deal_price字段）
            sign:         字符串 必填 RSA签名规则
    Returns:
        订单数据
    """
    out_order_no = str(params['out_order_no'])

    post_data = {
        'player_id': params['player_id'],
        'api_key': APP_KEY,
        'deal_price': '%.2f' % float(params['deal_price']),
        'deliver_type': '1',
        'notify_url': params['notify_url'],
        'out_order_no': out_order_no,
        'subject': params['subject'].encode('utf-8'),
        'submit_time': time.strftime('%Y%m%d%H%M%S'),
        'total_fee': '%.2f' % float(params['total_fee']),
    }
    exclude_keys = ('player_id',)
    sign_keys = sorted(post_data.iterkeys())
    sign_data = ''.join((post_data[k] for k in sign_keys if k not in exclude_keys))
    if isinstance(sign_data, unicode):
        sign_data.encode('utf-8')
    post_data['sign'] = utils.rsa_private_sign(PRIVATE_KEY, sign_data)

    _, content = http.post(CREATE_PAYMENT_ORDER_URL, json.dumps(post_data),
                           headers={'Content-Type': 'application/json'},
                           timeout=5)
    # print content
    return json.loads(content)


def payment_verify(req, params=None):
    """支付验证 out_order_no自定义
    Args:
        req: 验证需要的所有数据,以下是必须的
            api_key:      商户APIKey
            close_time:   支付订单关闭时间，格式为yyyyMMddHHmmss
            create_time:  支付订单创建时间，格式为yyyyMMddHHmmss
            deal_price:   浮点数 商品总金额
            out_order_no: 商户订单号
            pay_channel:  用户支付方式(A币支付：100，支付宝支付：101，财付通支付：103)
            submit_time:  商户提交订单时间，格式为yyyyMMddHHmmss
            user_id:      返回null
            sign:         以上字段按照顺序都参与签名，具体RSA签名规则
        params: 测试专用
    """
    if not params:
        params = {
            'api_key': req.get_argument('api_key', ''),
            'close_time': req.get_argument('close_time', ''),
            'create_time': req.get_argument('create_time', ''),
            'deal_price': req.get_argument('deal_price', '0.00'),
            'out_order_no': req.get_argument('out_order_no', ''),
            'pay_channel': req.get_argument('pay_channel', ''),
            'submit_time': req.get_argument('submit_time', ''),
            'user_id': req.get_argument('user_id', ''),
            'sign': req.get_argument('sign', ''),
        }

    exclude_keys = ('sign',)
    sign_keys = sorted((k for k in params if k not in exclude_keys))
    sign_values = []
    for k in sign_keys:
        v = params[k].encode('utf-8') if isinstance(params[k], unicode) else params[k]
        sign_values.append('%s=%s' % (k, v))
    sign_data = '&'.join(sign_values)
    if not utils.rsa_verify_signature(PUBLIC_KEY, sign_data, params['sign']):
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['out_order_no'],       # 自定义定单id
        'order_id': params['out_order_no'],           # 平台定单id
        'order_money': float(params['deal_price']),   # 平台实际支付money 单位元
        'uin': params['user_id'],                     # 平台用户id
        'platform': PLATFORM_NAME,                    # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    token = '{n:B4517033,v:918725B3AF80BC6039182374BD9311A43D8E9953,h:E0E3924B12F14AC4B6BCC903EF64554C,t:1432429136}'
    print login_verify('', params={'session_id': token, 'nickname': 'nickname'})
    post_data = {
        'player_id': 'h1232323',
        'deal_price': '6.00',
        'notify_url': 'http://dev.kaiqigu.net/genesis/pay/?method=callback&tp=jinli',
        'out_order_no': '29e0d905a798709b1530911d68313016',
        'subject': u"手机",
        'total_fee': '6.00',
    }
    #print create_pay_order(post_data)




