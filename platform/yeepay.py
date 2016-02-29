# coding: utf-8

PLATFORM_YEEPAY_SECERT_KEY = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
PLATFORM_YEEPAY_ENABLE = True
PLATFORM_YEEPAY_CMD = 'Buy'
PLATFORM_YEEPAY_MERID = '111111111'
PLATFORM_YEEPAY_NEED_RESPONSE = '1'
PLATFORM_YEEPAY_CURRENCY = 'CNY'
PLATFORM_YEEPAY_PRODUCT_NAME = 'product_name'
PLATFORM_YEEPAY_PRODUCT_TYPE = 'product_coin'
PLATFORM_YEEPAY_COMMAND_URL = 'https://www.yeepay.com/app-merchant-proxy/node'


def yeepay_pay(user_id, amount, kcoin, channel, product_id):
    """ 易宝支付请求
    Args:
        user_id: 用户id
        amount: 支付金额
        kcoin: 购买的酷币数量
        channel: 支付渠道
        product_id: 支付的商品id
    Returns:
        支付结果
    """
    params = {
        'p0_Cmd': PLATFORM_YEEPAY_CMD,
        'p1_MerId': PLATFORM_YEEPAY_MERID,
        'p2_Order': "%d_%s_%d_%d" % (time.time(), user_id, amount, kcoin),
        'p3_Amt': amount,
        'p4_Cur': PLATFORM_YEEPAY_CURRENCY,
        'p5_Pid': PLATFORM_YEEPAY_PRODUCT_NAME,
        'p6_Pcat': PLATFORM_YEEPAY_PRODUCT_TYPE,
        'p7_Pdesc': '%s %s' % (PLATFORM_YEEPAY_PRODUCT_TYPE,
                               PLATFORM_YEEPAY_PRODUCT_NAME),
        'p8_Url': PLATFORM_YEEPAY_RETURN_URL,
        'pa_MP': '%s,%d,%s' % (user_id, amount, product_id),
        'pd_FrpId': channel,
        'pr_NeedResponse': PLATFORM_YEEPAY_NEED_RESPONSE
    }

    data = ("%(p0_Cmd)s"
            "%(p1_MerId)s"
            "%(p2_Order)s"
            "%(p3_Amt)s"
            "%(p4_Cur)s"
            "%(p5_Pid)s"
            "%(p6_Pcat)s"
            "%(p7_Pdesc)s"
            "%(p8_Url)s"
            "%(pa_MP)s"
            "%(pd_FrpId)s"
            "%(pr_NeedResponse)s") % params

    params['hmac'] = hmac.new(PLATFORM_YEEPAY_SECERT_KEY, data).hexdigest()

    return "%s?%s" % (PLATFORM_YEEPAY_COMMAND_URL, urllib.urlencode(params))


def payment_verify(params):
    """ 易宝支付接口
    """
    obj = {
        'p1_MerId': PLATFORM_YEEPAY_MERID,
        'r0_Cmd': params['r0_Cmd'],
        'r1_Code': params['r1_Code'],
        'r2_TrxId': params['r2_TrxId'],
        'r3_Amt': params['r3_Amt'],
        'r4_Cur': params['r4_Cur'],
        'r5_Pid': params['r5_Pid'],
        'r6_Order': params['r6_Order'],
        'r7_Uid': params['r7_Uid'],
        'r8_MP': params['r8_MP'],
        'r9_BType': params['r9_BType'],
        'hmac': params['hmac']
    }

    data = ("%(p1_MerId)s"
            "%(r0_Cmd)s"
            "%(r1_Code)s"
            "%(r2_TrxId)s"
            "%(r3_Amt)s"
            "%(r4_Cur)s"
            "%(r5_Pid)s"
            "%(r6_Order)s"
            "%(r7_Uid)s"
            "%(r8_MP)s"
            "%(r9_BType)s") % params

    hmac_data = hmac.new(PLATFORM_YEEPAY_SECERT_KEY, data).hexdigest()
    if hmac_data != params['hmac']:
        return False

    #user_id, amount, product_id = params['r8_MP'].split(',')

    return obj

