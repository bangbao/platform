# coding: utf-8

#
# T-STORE平台注册应用ID
# TSTORE_APPID = ''

# 支付验证票据地址，分为正式环境和开发环境
# PRD_VERIFY_URL = 'https://iap.tstore.co.kr/digitalsignconfirm.iap'
# DEV_VERIFY_URL = 'https://iapdev.tstore.co.kr/digitalsignconfirm.iap'

# 定单数据样例:
#     {
#         "status" : 0,                    # 定单状态， 0表示成功，其它失败
#         "detail" : "0000",
#         "message" : "Normally Verified",
#         “count”: 1,
#         “product”: [
#             {
#             "log_time" : "20120321154451",      # 定单时间
#             "appid" : "aaaaaaaaa",             # 应用ID
#             "product_id" : "0900012345",        # 商品ID
#             "charge_amount" : 1000,             # 充值金额
#             “tid” : ”AFEDDFEFE!@dFDFfFFFF”  # 定单ID
#             "detail_pname" : "X",               # 商品描述
#             "bp_info" : "X"                     # 自定义字段
#             }
#         ]
#     }

import json
from helper import utils

DEBUG = True
if DEBUG:
    PLATFORM_TSTORE_VERIFY_URL = 'https://iapdev.tstore.co.kr/digitalsignconfirm.iap'
else:
    PLATFORM_TSTORE_VERIFY_URL = 'https://iap.tstore.co.kr/digitalsignconfirm.iap'
PLATFORM_TSTORE_APPID = '1111111'


def login_verify(token):
    return token


def payment_verify(params):
    """T-STORE平台充值验证验证充值票据信息
    Args:
        txid: 票据ID
        receipt: 票据签名
    Returns:
        票据信息
    """
    txid = params.get('txid')
    receipt = params.get('receipt')

    post_data = json.dumps({
        'appid': PLATFORM_TSTORE_APPID,
        'txid': txid,
        'signdata': receipt,
    })

    code, content = utils.http.post(PLATFORM_TSTORE_VERIFY_URL, post_data,
                                    headers={"Content-type": "application/json"},
                                    timeout=30)

    if code != 200:
        return None

    result = json.loads(content)

    if result['status'] != 0 or not result.get('product'):
        return None

    return result

