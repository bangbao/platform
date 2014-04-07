# coding: utf-8

import utils
import json
import time
import hashlib

DEBUG = True
if DEBUG:
    PLATFORM_UC_SERVER_URL = 'http://sdk.test4.g.uc.cn/ss'
else:
    PLATFORM_UC_SERVER_URL = 'http://sdk.g.uc.cn/ss'

PLATFORM_UC_CPID = 123
PLATFORM_UC_GAMEID = 111111
PLATFORM_UC_CHANNELID = 1
PLATFORM_UC_SERVERID = 1111
PLATFORM_UC_APIKEY = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaa'
PLATFORM_UC_SERVICE_USER_SIDINFO = 'ucid.user.sidInfo'
PLATFORM_UC_SERVICE_BIND_CREATE = 'ucid.bind.create'
PLATFORM_UC_GAMEINFO = {
    'cpId': PLATFORM_UC_CPID,
    'gameId': PLATFORM_UC_GAMEID,
    'channelId': PLATFORM_UC_CHANNELID,
    'serverId': PLATFORM_UC_SERVERID,
}


def login_verify(sid):
    """sid用户会话验证
    Args:
        sid: 从游戏客户端的请求中获取的sid值
    """
    data = {'sid': sid}

    post_data = {
        'id': int(time.time()),
        'service': PLATFORM_UC_SERVICE_USERSIDINFO,
        'data': data,
        'game': PLATFORM_UC_GAMEINFO,
        'sign': uc_generate_sign(data),
    }

    http_code, content = utils.http.post(PLATFORM_UC_SERVER_URL,
                                         body=json.dumps(post_data),
                                         timeout=30)

    if http_code != 200:
        return None

    obj = json.loads(content)
    if obj['state']['code'] != 1:
        return None

    return obj['data']['ucid']


def ucid_bind_create(self, game_user):
    """ucid和游戏官方帐号绑定接口
    :param game_user: 游戏官方帐号
    """
    data = {'gameUser': game_user}

    post_data = {
        'id': int(time.time()),
        'service': PLATFORM_UC_SERVICE_BIND_CREATE,
        'data': data,
        'game': PLATFORM_UC_GAMEINFO,
        'sign': uc_generate_sign(data),
    }

    http_code, content = utils.http.post(PLATFORM_UC_SERVER_URL,
                                         body=json.dumps(post_data),
                                         timeout=30)

    if http_code != 200:
        return None

    obj = json.loads(content)
    if obj['state']['code'] != 1:
        return None

    return obj['data']['ucid']


def payment_verify(post_data):
    """post_data 为回调post数据
    callbackInfo
    """
    dict_data = json.loads(post_data)

    sign = uc_generate_sign(dict_data['data'])

    if sign != dict_data['sign']:
        return False

    if dict_data['data']['orderStatus'] != "S":
        #支付状态不成功
        return False

    return dict_data


def uc_generate_sign(data):
    """生成sign
    """
    sorted_data = sorted(data.iteritems(), key=lambda x : x[0], reverse=False)
    list_data = ['%s=%s' % (str(k), str(v)) for k, v in sorted_data]
    sign_str = '%s%s%s' % (PLATFORM_UC_CPID, ''.join(list_data), PLATFORM_UC_APIKEY)

    return hashlib.md5(sign_str).hexdigest()

