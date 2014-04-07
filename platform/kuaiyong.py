# coding: utf-8

import utils
import base64

PLATFORM_KUAIYONG_APP_ID = '1111'
PLATFORM_KUAIYONG_APP_SECRET = "aaaaaaaaaaaaaaaaaaaaaaaa"
PLATFORM_KUAIYONG_APP_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
....
-----END PUBLIC KEY-----"""


def login_verify(token):
    return token


def payment_verify(params):
    """支付验证
    Args:
        params: 字典参数数据
    Returns:
        订单数据
    """
    sign = params['sign']
    notify_data = params["notify_data"]

    decrypt_data = utils.rsa_public_decrypt(PLATFORM_KUAIYONG_APP_PUBLIC_KEY, notify_data)
    obj = dict(utils.parse_cgi_data(decrypt_data))

    if int(obj["payresult"]) != 0 or params["dealseq"] != obj["dealseq"]:
        return False

    sign_keys = ("dealseq", "notify_data", "orderid", "subject", "uid", "v")
    sign_list = ('%s=%s' % (k, params[k]) for k in sign_keys)
    sign_data =  '&'.join(sign_list)

    if not utils.rsa_verify_signature2(APP_PUBLIC_KEY, sign_data, sign):
        return False

    return obj

