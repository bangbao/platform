# encoding: utf-8

import json
import urllib
from helper import http
from helper import utils

__VERSION__ = '1.2.6'
PLATFORM_NAME = 'iiapple'
GAME_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxx'
SERCET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
APP_USERINFO_URL = 'http://ucenter.iiapple.com/foreign/oauth/verification.php'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: {"status": 0, "transIDO": ''},
    1: {"status": 1, "transIDO": ''},
}


def login_verify(req, params=None):
    """登录验证
    Args:
        req: request封装，以下是验证所需参数
            session_id: 用户 session
            user_id: 用户 id
        params: 测试专用
    Returns:
        平台相关信息(openid必须有)
    """
    if not params:
        params = {
            'session_id': req.get_argument('session_id', ''),
            'user_id': req.get_argument('user_id', ''),
        }
    session = params['session_id']
    user_id = params['user_id']
    nickname = user_id

    sign_data = {
        'session': session,
        'user_id': user_id,
        'game_id': GAME_KEY,
    }
    sign_data1 = '&'.join('%s=%s' % (k, v) for k, v in sorted(sign_data.iteritems()))
    sign_data2 = '%s%s' % (utils.hashlib_md5_sign(sign_data1), SERCET_KEY)
    sign_data['_sign'] = utils.hashlib_md5_sign(sign_data2)

    query_data = urllib.urlencode(sign_data)
    url = '%s?%s' % (APP_USERINFO_URL, query_data)
    http_code, content = http.get(url)
    #print '%s %s' % (http_code, content)
    if http_code != 200:
        return None

    obj = json.loads(content)
    # {"desc":"合作方不存在","status":"1000001"}
    if int(obj['status']) != 1:
        return None

    return {
        'openid': user_id,      # 平台标识
        'openname': nickname,   # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            transaction:    交易流水号
            payType:        支付方式
            userId:         充值中心用户ID。
            serverNo:       研发方服务器编号
            amount          金额,单位是元
            cardPoint:      点数
            gameUserId:     游戏用户唯一标识
            transactionTime:订单交易时间
            gameExtend:     研发方需要的扩展参数
            platform:       充值中心表示GW
            status:         状态 :返回 1 表示成功
            currency:       货币类型( CNY)
            _sign:          签名
        params: 测试专用
    """
    if not params:
        params = {
            'transaction': req.get_argument('transaction', ''),
            'payType': req.get_argument('payType', ''),
            'userId': req.get_argument('userId', ''),
            'serverNo': req.get_argument('serverNo', ''),
            'amount': req.get_argument('amount', ''),
            'cardPoint': req.get_argument('cardPoint', ''),
            'gameUserId': req.get_argument('gameUserId', ''),
            'transactionTime': req.get_argument('transactionTime', ''),
            'gameExtend': req.get_argument('gameExtend', ''),
            'platform': req.get_argument('platform', ''),
            'status': req.get_argument('status', 1),
            'currency': req.get_argument('currency', ''),
            '_sign': req.get_argument('_sign', ''),
        }

    # 生成返回数据
    return_data = {}
    for code, data in RETURN_DATA.iteritems():
        return_data[code] = dict(data, transIDO=params['transaction'])

    # 充值状态：1 表示成功
    if int(params['status']) != 1:
        return_data[1] = return_data[0]
        return return_data, None

    exclude = ('_sign',)
    sign_items = sorted([(key, value) for key, value in params.iteritems() if key not in exclude])
    sign_data1 = '&'.join('%s=%s' % (key, value) for key, value in sign_items)
    sign_data2 = '%s%s' % (utils.hashlib_md5_sign(sign_data1), SERCET_KEY)
    new_sign = utils.hashlib_md5_sign(sign_data2)

    if new_sign != params['_sign']:
        return return_data, None

    pay_data = {
        'app_order_id': params['gameExtend'],        # 自定义定单id
        'order_id': params['transaction'],           # 平台定单id
        'order_money': float(params['amount']),      # 平台实际支付money 单位元
        'uin': params['userId'],                     # 平台用户id
        'platform': PLATFORM_NAME,                   # 平台标识名
    }
    return return_data, pay_data


if __name__ == '__main__':
    print login_verify('', {'user_id': '', 'session_id': ''})

