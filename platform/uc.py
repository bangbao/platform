# coding: utf-8

import json
import time
from helper import http
from helper import utils

__VERSION__ = '1.2.4'
PLATFORM_NAME = 'uc'
#CPID = 54720
GAMEID = 551131
#CHANNELID = 2   # 渠道编号,传入字符串 2即可
#SERVERID = 0    # 服务器编号,如果没有请填写 0
APIKEY = 'xxxxxxxxxxxxxxxxxxxxxxx'
SERVER_URL = 'http://sdk.g.uc.cn/cp/account.verifySession'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'SUCCESS',
    1: 'FAILURE',
}


def login_verify(req, params=None):
    """登录验证
    Args:
        req: request封装，以下是验证所需参数
            session_id: 32 位字符串
        params: 测试专用
    Returns:
        平台相关信息(openid必须有)
    """
    if not params:
        params = {
            'session_id': req.get_argument('session_id'),
        }
    sid = params['session_id']

    sign_str = 'sid=%s%s' % (sid, APIKEY)
    sign = utils.hashlib_md5_sign(sign_str)
    post_data = json.dumps({
        'id': int(time.time()),
        'data': {'sid': sid},
        'game': {'gameId': GAMEID},
        'sign': sign,
    })
    http_code, content = http.post(SERVER_URL, post_data)
    #print http_code, content
    if http_code != 200:
        return None

    # {"id":1428398099,"state":{"code":1,"msg":"操作成功"},
    #  "data":{"accountId":"b761bbe6e2878fd6cb76541f072092ed",
    #  "nickName":"九游玩家645635397","creator":"JY"}}
    obj = json.loads(content)
    if obj['state']['code'] != 1:
        return None

    return {
        'openid': obj['data']['accountId'],         # 平台标识
        'openname': obj['data']['nickName'],        # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            post_data: 为uc回调post数据， json格式
                ver: 接口版本号,2.0
                sign: 签名
                data: 支付票据
                    orderId: UC充值订单号
                    gameId: 游戏编号
                    accountId: 账号标识
                    creator: 账号的创建者 JY:九游 PP:PP 助手
                    payWay: 支付通道代码
                    amount: 支付金额 单位:元。
                    callbackInfo: 游戏合作商自定义参数
                    orderStatus: 订单状态 S-成功支付 F-支付失败
                    failedDesc: 订 单 失 败 原 因 string 详细描述 Y 如果是成功支付,则为空串。
                    cpOrderId: Cp 订单号 仅当客户端调用支付方法传入了transactionNumCP 参数时,
                                才会将原内容通过 cpOrderId 参数透传回游戏服务端。
        params: 测试专用
    """
    if not params:
        post_data = req.request.body
        try:
            params = json.loads(post_data)
        except ValueError:
            return RETURN_DATA, None

    if params['data']['orderStatus'] != "S":
        result = dict(RETURN_DATA)
        result[1] = result[0]
        return result, None

    data = params['data']
    data['gameId'] = GAMEID
    data['apiKey'] = APIKEY
    sign_str = ('accountId=%(accountId)s'
                'amount=%(amount)s'
                'callbackInfo=%(callbackInfo)s'
                #'cpOrderId=%(cpOrderId)s'
                'creator=%(creator)s'
                'failedDesc=%(failedDesc)s'
                'gameId=%(gameId)s'
                'orderId=%(orderId)s'
                'orderStatus=%(orderStatus)s'
                'payWay=%(payWay)s'
                '%(apiKey)s') % data
    new_sign = utils.hashlib_md5_sign(sign_str)
    if new_sign != params['sign']:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': data['callbackInfo'],    # 自定义定单id
        'order_id': data['orderId'],             # 平台定单id
        'order_money': float(data['amount']),    # 平台实际支付money 单位元
        'uin': data['accountId'],                # 平台用户id
        'platform': PLATFORM_NAME,               # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    print login_verify('', {'session_id': 'ssh1mobie063b7320a834290bfe16a8f6a2703ab101368'})


