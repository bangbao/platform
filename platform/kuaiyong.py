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
    """
    """
    sign = params['sign']
    notify_data = params["notify_data"]

    decrypt_verify_data = utils.rsa_public_decrypt(PLATFORM_KUAIYONG_APP_PUBLIC_KEY, notify_data)
    obj = {a_s.split("=")[0]: a_s.split("=")[1] for a_s in decrypt_verify_data.split("&")}

    if int(obj["payresult"]) != 0 or params["dealseq"] != obj["dealseq"]:
        return False

    key_list = ["dealseq", "notify_data", "orderid", "subject", "uid", "v"]
    list_data = ['%s=%s' % (str(k), str(data[k])) for k in key_list]
    verify_data =  '&'.join(list_data)
    sign = data["sign"]
    
    if not utils.rsa_verify_signature2(APP_PUBLIC_KEY, verify_data, sign):
        return False

    return obj

