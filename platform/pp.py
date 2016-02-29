# coding: utf-8

import json
import time
from helper import http
from helper import utils

__VERSION__ = '1.4.3'
PLATFORM_NAME = 'pp'
APP_ID = '1111'
APP_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu/nvFcF8nIai164SuOUb
UB795u2U/ho1duPe6gm3NweWubD/spZNx5bqdRcM62dJ48YKJoE8AyMEDMoUMy+M
oikH68mGFF8R5EnetADfhKd6YdO87AI+M8acOm01/oBTkkYgb4+FWxjNf2s7Zfsv
h3JdzDaE76kuc950X8F3jnFNT3C2ff2VQAllJFwn4lJPi7lhN0jyHGQAC+9k9fOJ
FLYOeUbj6YGugyvob1uxBG3XpnctuI49LMdFr6e104ewcF57Ao2hGXKaUlXXHSPj
V6ea2bGzCH4Fd3BZF9phTQ8+zZeNczgRgyy6p/I71RT9WR2Ve7gO02BuMcOUPren
LwIDAQAB
-----END PUBLIC KEY-----"""
GET_USERINFO_URL = 'http://passport_i.25pp.com:8080/account?tunnel-command=2852126760'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'success',
    1: 'fail',
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
    session_id = params['session_id']

    sign_str = 'sid=%s%s' % (session_id, APP_KEY)
    post_data = json.dumps({
        'id': int(time.time()),
        'service': 'account.verifySession',
        'data': {'sid': session_id},
        'game': {'gameId': APP_ID},
        'encrypt': 'md5',
        'sign': utils.hashlib_md5_sign(sign_str),
    })
    headers = {'Content-type': 'application/json;charset=utf-8'}
    # 对方服务器经常timeout
    try:
        http_code, content = http.post(GET_USERINFO_URL, post_data, headers=headers, timeout=1)
        #print http_code, content
    except:
        return None
    if http_code != 200:
        return None

    result = json.loads(content)
    if int(result['state']['code']) != 1:
        return None

    data = result['data']
    openid = data['accountId']
    if data['creator'] != 'PP':
        openid = '%s%s' % (data['creator'], openid)

    return {
        'openid': openid,                  # 平台标识
        'openname': data['nickName'],      # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            order_id: 兑换订单号
            billno:   厂商订单号(原样返回给游戏服)
            account:  通行证账号
            amount:   兑换 PP 币数量
            status:   状态: 是 0 正常状态 1 已兑换过并成功返回
            app_id:   厂商应用 ID(原样返回给游戏服)
            uuid:     设备号(返回的 uuid 为空)
            roleid:   厂商应用角色 id(原样返回给游戏服)
            zone:     厂商应用分区 id(原样返回给游戏服)
            sign:     签名(RSA 私钥加密) 是
        params: 测试专用
    """
    if not params:
        params = {
            'order_id': req.get_argument('order_id', ''),
            'billno': req.get_argument('billno', ''),
            'account': req.get_argument('account', ''),
            'amount': req.get_argument('amount', '0'),
            'status': int(req.get_argument('status', 1)),
            'app_id': req.get_argument('app_id', ''),
            'roleid': req.get_argument('roleid', ''),
            'uuid': req.get_argument('uuid', ''),
            'zone': req.get_argument('zone', ''),
            'sign': req.get_argument('sign', ''),
        }

    if not params['sign'] or not params['billno']:
        return RETURN_DATA, None

    if int(params['status']) != 0:
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    ctxt = utils.rsa_public_decrypt(PUBLIC_KEY, params['sign'])
    order_sign = json.loads(ctxt)
    for k, v in order_sign.iteritems():
        if v != params[k]:
            return RETURN_DATA, None

    pay_data = {
        'app_order_id': params['billno'],         # 自定义定单id
        'order_id': params['order_id'],           # 平台定单id
        'order_money': float(params['amount']),   # 平台实际支付money 单位元
        'uin': params['account'],                 # 平台用户id
        'platform': PLATFORM_NAME,                # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    print login_verify('', {'session_id': '856b8e5424398602d8ef8d6a88fd02af'})




