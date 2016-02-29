# coding: utf-8

import hashlib
from helper import http

PLATFORM_NAME = 'lvan'
ID = 1649
APP_KEY = 'xxxxxxxxxxxxxxxxxx'
APP_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
VERIFY_LOGIN_URL = 'http://auth.3636.com/r/validation/'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'success',
    1: 'fail',
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
            'nickname': req.get_argument('nickname', ''),
        }
    token = params['session_id']
    uid = params['user_id']
    nickname = params['nickname']

    url = '%s%s/%s' % (VERIFY_LOGIN_URL, uid, token)
    http_code, content = http.get(url)

    if http_code != 200:
        return None

    # “OK”：验证登录成功 “FAILE”：验证登录失败
    if content != 'OK':
        return None

    return {
        'openid': uid,             # 平台用户ID
        'openname': nickname,      # 平台用户名字
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            r01_uid:              充值账号 ID
            r02_orderId:          支付中心订单 ID
            r03_pid:              商品（道具）ID
            r04_pname:            商品名称
            r05_status:           订单状态
            r06_amount:           充值金额
            r07_gameZone:         充值大区
            r08_appId:            应用 ID
            r09_createOrderTime:  订单创建时间
            r10_outTradeNo:       商户订单号
            r11_payTime:          支付时间
            r12_extInfo:          自定义信息
            sign:                 签名
        params: 测试专用
    Returns:
        return_data: 返回数据
            成功和失败的数据
        pay_data: 支付数据
            app_order_id: 自定义定单id
            order_id: 平台定单id
            order_money: 平台实际支付money
            uin: 平台用户id
            platform: 平台标识
    """
    if not params:
        params = {
            'r01_uid': req.get_argument('r01_uid', ''),
            'r02_orderId': req.get_argument('r02_orderId', ''),
            'r03_pid': req.get_argument('r03_pid', ''),
            'r04_pname': req.get_argument('r04_pname', ''),
            'r05_status': req.get_argument('r05_status', ''),
            'r06_amount':req.get_argument('r06_amount', ''),
            'r07_gameZone':req.get_argument('r07_gameZone', ''),
            'r08_appId':req.get_argument('r08_appId', ''),
            'r09_createOrderTime':req.get_argument('r09_createOrderTime', ''),
            'r10_outTradeNo':req.get_argument('r10_outTradeNo', ''),
            'r11_payTime':req.get_argument('r11_payTime', ''),
            'r12_extInfo':req.get_argument('r12_extInfo', ''),
            'sign':req.get_argument('sign','')
        }
    if not params['sign']:
        return RETURN_DATA, None

    sign_keys = ('r01_uid','r02_orderId','r03_pid','r04_pname','r05_status','r06_amount','r07_gameZone',
                    'r08_appId','r09_createOrderTime','r10_outTradeNo','r11_payTime','r12_extInfo')
    sign_values = [str(params[key]) for key in sign_keys if params[key]]
    sign_values.append(APP_SECRET)
    sign_str = '&'.join(sign_values)
    new_sign = hashlib.md5(sign_str).hexdigest()

    if new_sign != params['sign']:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['r12_extInfo'],           # 自定义定单id
        'order_id': params['r02_orderId'],               # 平台定单id
        'order_money': float(params['r06_amount']),      # 平台实际支付money 单位元
        'uin': params['r01_uid'],                        # 平台用户id
        'platform': PLATFORM_NAME,                       # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    #print login_verify('540683828226441ab111194b2d2e3d0f')
    #params = {'user_id':'242964320','money':'1','order_no':'GP140903181559832144','sign':'8c707850b10cf11142614482463440a6','dd':'cc'}
    params = {}
    print payment_verify(params)
