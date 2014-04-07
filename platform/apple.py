# coding: utf-8

import utils
import json

DEBUG = True

if not DEBUG:
    APPLE_VERIFY_RECEIPTS_URL = 'https://buy.itunes.apple.com/verifyReceipt'
else:
    APPLE_VERIFY_RECEIPTS_URL = 'https://sandbox.itunes.apple.com/verifyReceipt'


def login_verify(token):
    """
    """
    return token


def payment_verify(receipt_data):
    """receipt-data 为apple前端支付后回来的票据， 已用base64编码
    """
    code, content = utils.http.post(APPLE_VERIFY_RECEIPTS_URL,
                                    body=json.dumps({'receipt-data': receipt_data}),
                                    headers={"Content-type": "application/json"},
                                    validate_cert=False)
    if code != 200:
        return False

    result = json.loads(content)
    receipt = result.get('receipt')

    if not receipt or result['status'] != 0:
        return False

    return receipt

