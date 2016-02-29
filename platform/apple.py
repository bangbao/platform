# coding: utf-8

import json
from helper import http

PLATFORM_NAME = 'apple'
# 正式环境支付票据验证地址
APPLE_VERIFY_RECEIPTS_URL = 'https://buy.itunes.apple.com/verifyReceipt'
# 沙箱环境支付票据验证地址
APPLE_SANDBOX_VERIFY_RECEIPTS_URL = 'https://sandbox.itunes.apple.com/verifyReceipt'
# 验证成功状态值
APPLE_VERIFY_SUCCESS_STATUS = 0


def login_verify(token):
    """
    """
    return token


def payment_verify(receipt_data, sandbox=False):
    """apple_store支付票据验证
    Args:
        receipt_data: 为apple前端支付后回来的票据， 已用base64编码
        sandbox: 是否是沙箱环境
    Returns:
        验证成功返回支付数据，失败返回None
    """
    #if sandbox:
    #    verify_url = APPLE_SANDBOX_VERIFY_RECEIPTS_URL
    #else:
    #    verify_url = APPLE_VERIFY_RECEIPTS_URL

    sandbox = False
    post_data = json.dumps({'receipt-data': receipt_data})
    headers = {"Content-type": "application/json"}
    http_code, content = http.post(APPLE_VERIFY_RECEIPTS_URL, post_data,
                                   headers=headers, validate_cert=False, timeout=5)
    if http_code != 200:
        return sandbox, None

    result = json.loads(content)
    if result['status'] == 21007:
        sandbox = True
        # The 21007 status code indicates that this receipt is a sandbox receipt,
        # but it was sent to the production service for verification.
        http_code, content = http.post(APPLE_SANDBOX_VERIFY_RECEIPTS_URL, post_data,
                                       headers=headers, validate_cert=False, timeout=5)
        if http_code != 200:
            return sandbox, None
        result = json.loads(content)

    receipt = result.get('receipt')
    if not receipt or result['status'] != APPLE_VERIFY_SUCCESS_STATUS:
        return sandbox, None

    return sandbox, receipt


if __name__ == '__main__':
    data = ''
    print payment_verify(data)


