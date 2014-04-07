# coding: utf-8

# 合作商户ID。用签约支付宝账号登录ms.alipay.com后，在账户信息页面获取。
# PARTNER = "1111111111111"

# 商户收款的支付宝账号
# SELLER = "alipay1@125.com"
# PAYMENT_CALLBACK_URL = /payment-callback-alipay/

# 定单数据样例:
#     {
#       u'trade_no': u'2013071738824025',                # 定单号
#       u'seller_email': u'alipay-test09@alipay.com',    # 商家帐号
#       u'seller_id': u'2088101568358171',               # 商家ID
#       u'trade_status': u'TRADE_SUCCESS',               # 交易状态
#       u'is_total_fee_adjust': u'N',
#       u'gmt_create': u'2013-07-17 15:26:18',
#       u'price': u'1.00',
#       u'buyer_email': u'yanbo_py@126.com',             # 消费者帐号
#       u'use_coupon': u'N',
#       u'discount': u'0.00',
#       u'out_trade_no': u'a00aaa017_1374045885668_60_0',# 自定义定单号
#       u'notify': u'N',
#       u'payment_type': u'8',
#       u'total_fee': u'1.00',                           # 消费钱数
#       u'partner': u'1111111111111111',                 # 合作者Id, 与商家id一对多关系
#       u'quantity': u'1',
#       u'gmt_payment': u'2013-07-17 15:26:20',
#       u'buyer_id': u'2088902575820253',                # 消费者ID
#       u'subject': u'65\u5143\u5b9d'
#     }

import utils

# 支付宝支付
PLATFORM_NAME = 'alipay'
PLATFORM_ALIPAY_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
......
-----END PUBLIC KEY-----"""


def login_verify(token):
    """没有平台用户，用平台标识alipay加token标识用户
    """
    return 'alipay_%s' % token


def payment_verify(data):
    """rsa验证数据签名
    Args:
        signedData: 要验证的数据
        signature: 签名
    Returns:
        布尔值，True表示验证通过，False表示验证失败
    """
    sign = data['sign']
    notify_data = data['notify_data']
    signed_data = 'notify_data=%s' % notify_data

    if not utils.rsa_verify_signature(PLATFORM_ALIPAY_PUBLIC_KEY, signed_data, sign):
        return False

    obj = utils.xml2dict(notify_data)
    if obj['trade_status'] not in ('TRADE_SUCCESS', 'WAIT_BUYER_PAY'):
        return False

    return obj
