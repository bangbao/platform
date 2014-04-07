# coding: utf-8

import utils
import json
import hashlib

PLATFORM_NAME = 'ggplay'
PLATFORM_GGPLAY_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
....
-----END PUBLIC KEY-----"""


def login_verify(token):
    return token


def payment_verify(signature_data):
    """ google_play 支付验证接口
    Args:
        signature_data: 支付票据
    """
    signature_data = urllib.unquote(signature_data)

    params = dict(logics.parse_signature_data(signature_data))
    signed_data = params.get('signedData', '')
    signature = params.get('signature', '')

    if not utils.rsa_verify_signature(GOOGLE_PLAY_PUBLIC_KEY, signed_data, signature):
        return False

    data = json.loads(signed_data)

    for obj in data['orders']:
        if obj['purchaseState'] != 0:
            return False

    return data