# coding: utf-8

from helper import utils

__VERSION__ = 'v1.2.8'
PLATFORM_NAME = 'pps'
# APP_ID = '521'
# GAME_ID = '3210'
APP_KEY = 'xxxxxxxxxxxxxxxxxx'
PAYMENT_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxx'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: {'result': 0, 'message': 'success'},
    1: {'result': -1, 'message': 'sign error'},
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
            'user_id': req.get_argument('user_id', ''),
        }
    user_id = params['user_id']

    return {
        'openid': user_id,          # 平台用户ID
        'openname': user_id,        # 平台用户名字
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            user_id:  用户id
            role_id:  角色ID，没有传空
            order_id: 平台订单号（唯一）
            money:    充值金额（人民币，单位元）
            time:     时间戳 time()
            userData: 回传参数(urlencode)该参数内容为游戏方自定义内容
            sign:     经过加密后的签名，sign= MD5($user_id.$role_id.$order_id.$money.$time.$key)
        params: 测试专用
    """
    if not params:
        params = {
            'user_id': req.get_argument('user_id', ''),
            'role_id': req.get_argument('role_id', ''),
            'order_id': req.get_argument('order_id', ''),
            'money': req.get_argument('money', '0'),
            'time': req.get_argument('time', ''),
            'userData': req.get_argument('userData', ''),
            'sign': req.get_argument('sign', ''),
        }

    sign_str = '%s%s%s%s%s%s' % (params['user_id'], params['role_id'], params['order_id'],
                                 params['money'], params['time'], PAYMENT_KEY)
    new_sign = utils.hashlib_md5_sign(sign_str)
    if new_sign != params['sign']:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['userData'],              # 自定义定单id
        'order_id': params['order_id'],                  # 平台定单id
        'order_money': float(params['money']),           # 平台实际支付money 单位元
        'uin': params['user_id'],                        # 平台用户id
        'platform': PLATFORM_NAME,                       # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    # print login_verify('', {'user_id': 'user_id'})
    params = {'user_id': 'user_id', 'role_id': 'role_id', 'order_id': 'order_id',
              'money': '100', 'time': '14000000000', 'userData': 'g11123122-g11-3-14000000',
              'sign': 'sdfasdfasdfsdfsdfsdf'}
    print payment_verify('', params)

