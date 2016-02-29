# coding: utf-8

import json
import urllib
from helper import http
from helper import utils

__VERSION__ = '1.0.3'
PLATFORM_NAME = 'kuaiyong'
APP_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
#GAMEID = '7388'                               # 客户端用
#MD5KEY = 'E6XiCMSVKqjc0S2R4DvWAFRZgt1rfnYU'   # 客户端用
APP_RSA_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC14qOZBPEYNKB0I4Mm+/qbmkFE
lh/vIoKcJcwIDRZipPDD5UINkUMaggHQRYNFAa+yE5y2Yt9LvzTWDIs2qaKGKFGL
PZ/FsLKXxAal5+aDyXgTJtAktMPGeC9kY4EK4RA7GTw0PDLOss7hNmQ0J3v4O7cC
vTveROeLtG/NI8A2GQIDAQAB
-----END PUBLIC KEY-----"""
# APP_KEY = '7d4330d7077c4ff54567ce9f768e90a3'
# #GAMEID = '8390'                               # 客户端用
# #MD5KEY = 'VPj9C77lK2CmmaqD1ppSwWCu1F6gVvyR'   # 客户端用
APP_RSA_PUBLIC_KEY_OLD = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDhO9N09wT5h7sEdjvusUP9pETS
8Zl42wfcLj6Cd5OUMUdPukTZsaD91SSYf+/oFXT9AQljUg7NLBKHPwrwhbIl+KWD
zCXjMbCfi2X+geRKzCmMUQdIpfetw27YDH5bpsxCg7N47UrlLjgIIaLT9mjgzWYD
8F3I4PoU0JYmtf7XWwIDAQAB
-----END PUBLIC KEY-----"""
VERIFY_TOKEN_URL = 'http://f_signin.bppstore.com/loginCheck.php'
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
            'session_id': req.get_argument('session_id'),
        }
    token_key = params['session_id']

    query_data = urllib.urlencode({
        'tokenKey': token_key,
        'sign': utils.hashlib_md5_sign(APP_KEY + token_key),
    })
    http_code, content = http.post(VERIFY_TOKEN_URL, query_data)
    #print http_code, content
    if http_code != 200:
        return None

    obj = json.loads(content)
    # {"code":0,"msg":"\u53c2\u6570\u9519\u8bef","data":{"guid":"s1234567890","username":"testUser"}}
    if int(obj['code']) != 0:
        return None

    return {
        'openid': obj['data']['guid'],            # 平台用户ID
        'openname': obj['data']['username'],      # 平台用户名字
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            notify_data: RSA 加密的关键数据，解密后格式为：
                         dealseq=20130219160809567&fee=0.01&payresult=0；
                         其中 payresult 是支付结果：0：成功，-1：支付失败， -2 超时失败；
                         dealseq 是开发商交易号；
                         fee 是支付金额：支付成功时， 表示实际支付金额
            orderid:     快用平台订单号
            dealseq:     游戏订单号（透传，唯一开发商可以自定义的参数）
            uid:         快用平台用户GUID
            subject:     购买物品名
            v:           版本号（固定参数=1.0）
            sign:        RSA 签名。签名的原串，是将收到的除去 sign 这个值之外的参数，
                         根据key 值做排序组成的 url 参数形式，
        params: 测试专用
    """
    if not params:
        params = {
            'notify_data': req.get_argument('notify_data', ''),
            'orderid': req.get_argument('orderid', ''),
            'dealseq': req.get_argument('dealseq', ''),
            'uid': req.get_argument('uid', ''),
            'subject': req.get_argument('subject', ''),
            'v': req.get_argument('v', ''),
            'sign': req.get_argument('sign', ''),
        }
    sign = params['sign']
    notify_data = params["notify_data"]

    if not sign or not notify_data:
        return RETURN_DATA, None

    public_key = APP_RSA_PUBLIC_KEY
    # TODO 更新参数后保证老参数在一定时间内可用
    try:
        decrypt_data = utils.rsa_public_decrypt(public_key, notify_data)
    except:
        public_key = APP_RSA_PUBLIC_KEY_OLD
        decrypt_data = utils.rsa_public_decrypt(public_key, notify_data)

    #decrypt_data = utils.rsa_public_decrypt(public_key, notify_data)
    obj = dict(utils.parse_cgi_data(decrypt_data))

    if int(obj["payresult"]) != 0:
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    # 根据key做排序
    sign_keys = ("dealseq", "notify_data", "orderid", "subject", "uid", "v")
    sign_list = ('%s=%s' % (k, params[k]) for k in sign_keys)
    sign_data = '&'.join(sign_list)
    if isinstance(sign_data, unicode):
        sign_data = sign_data.encode('utf-8')

    if not utils.rsa_verify_signature(public_key, sign_data, sign):
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['dealseq'],          # 自定义定单id
        'order_id': params['orderid'],              # 平台定单id
        'order_money': float(obj['fee']),           # 平台实际支付money 单位元
        'uin': params['uid'],                       # 平台用户id
        'platform': PLATFORM_NAME,                  # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    params = {'session_id': 'cd19f2950af4183b2ddc30e462dcf704'}
    print login_verify('', params)


