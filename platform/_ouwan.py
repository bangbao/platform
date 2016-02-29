# coding: utf-8

from helper import utils

PLATFORM_NAME = 'ouwan'
APP_KEY = 'xxxxxxxxxxxxxxxx'
APP_SECRET = 'xxxxxxxxxxxxxxxxxxxx'
SERVER_SECRET = 'xxxxxxxxxxxxxxxxxxx'
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
            'session_id': req.get_argument('session_id', ''),
            'user_id': req.get_argument('user_id', ''),
            'nickname': req.get_argument('nickname', '')
        }
    sign = params['session_id']
    openid = params['user_id']
    timestamp = params['nickname']

    #验证
    sign_str = '%s&%s&%s' % (openid, timestamp, SERVER_SECRET)
    new_sign = utils.hashlib_md5_sign(sign_str)
    if sign != new_sign:
        return None

    return {
        'openid': openid,          # 平台用户ID
        'openname': openid,        # 平台用户名字
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            serverId :    充值的时候传入的ID
            callbackInfo: SDK调用充值时传入的透传
            openId:       充值用户标识ID
            orderId:      偶玩订单唯一ID
            orderStatus:  充值状态 1表示成功，　其它失败
            payType:      用户支付方式
            amount:       用户充值金额
            remark:       错误信息
            sign:         签名
        params: 测试专用
    """
    if not params:
        params = {
            'serverId': req.get_argument('serverId', ''),
            'callbackInfo': req.get_argument('callbackInfo', ''),
            'openId': req.get_argument('openId', ''),
            'orderId': req.get_argument('orderId', ''),
            'orderStatus': req.get_argument('orderStatus', ''),
            'payType':req.get_argument('payType',''),
            'amount': req.get_argument('amount', ''),
            'remark': req.get_argument('remark', ''),
            'sign': req.get_argument('sign',''),
        }

    #orderStatus = 1 订单成功，其他订单失败
    if str(params['orderStatus']) != '1':
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    sign = params.pop('sign', '')

    sign_list = []
    for k, v in sorted(params.iteritems()):
        sign_list.append('%s=%s' % (k, v))
    sign_list.append(SERVER_SECRET)
    sign_str = ''.join(sign_list)
    new_sign = utils.hashlib_md5_sign(sign_str)
    if new_sign != sign:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['callbackInfo'],         # 自定义定单id
        'order_id': params['orderId'],                  # 平台定单id
        'order_money': float(params['amount']),         # 平台实际支付money 单位元
        'uin': params['openId'],                        # 平台用户id
        'platform': PLATFORM_NAME,                      # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    #print login_verify('540683828226441ab111194b2d2e3d0f')
    #params = {'user_id':'242964320','money':'1','order_no':'GP140903181559832144','sign':'8c707850b10cf11142614482463440a6','dd':'cc'}
    params = {'serverId':'g62922441','callbackInfo':'g62922441-q1-1-1410510032483','openId':'7c01ab3971f93c5b','orderId':'m201409121621291000285','orderStatus':'1','payType':'ALIPAY','amount':'1','remark':'','sign':'389205cf0707eaba7f29a5632d2985f5'}
    print payment_verify('', params)


