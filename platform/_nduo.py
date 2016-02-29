# coding: utf-8

from helper import utils

PLATFORM_NAME = 'nduo'
APP_KEY = 'xxxxxxxxxx'
PAY_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
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
            'user_id': req.get_argument('user_id', ''),
            'nickname': req.get_argument('nickname', ''),
        }
    user_id = params['user_id']
    nickname = params['nickname']

    if not user_id:
        return None

    return {
        'openid': user_id,          # 平台用户ID
        'openname': nickname,       # 平台用户名字
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            nduoTradeNo: N多网订单号，32位字符串
            appTradeNo： 接入方订单号
            appKey:      当前app在N多接入后台申请的key
            userToken：  n多用户唯一标识，32为字符串
            amount：     充值金额，单位为分
            server：     生成订单的服务器编号
            serverName： 生成订单的服务器名称
            subject：    商品名称
            body：       商品描述
            sign：       MD5签名字符串
        params: 测试专用
    """
    if not params:
        params = {
            'nduoTradeNo': req.get_argument('nduoTradeNo', ''),
            'appTradeNo': req.get_argument('appTradeNo', ''),
            'appKey': req.get_argument('appKey', ''),
            'userToken':req.get_argument('userToken',''),
            'amount':req.get_argument('amount', ''),
            'server':req.get_argument('server',''),
            'serverName':req.get_argument('serverName',''),
            'subject':req.get_argument('subject',''),
            'body': req.get_argument('body', ''),
            'sign':req.get_argument('sign',''),
        }

    sorted_params = sorted([(k, v.encode('utf-8') if isinstance(v, unicode) else v)
                                for k, v in params.iteritems() if k != 'sign'])
    sign_values = '&'.join(['%s=%s' % (k, v) for k, v in sorted_params])
    sign_values += PAY_KEY
    new_sign = utils.hashlib_md5_sign(sign_values)
    if new_sign != params['sign']:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['appTradeNo'],            # 自定义定单id
        'order_id': params['nduoTradeNo'],               # 平台定单id
        'order_money': float(params['amount']) / 100,    # 平台实际支付money 单位元
        'uin': params['userToken'],                      # 平台用户id
        'platform': PLATFORM_NAME,                       # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    pass
