# coding: utf-8

"""
使用JPush来发送推送
服务器API文档地址： http://docs.jpush.cn/display/dev/Push-API-v3
"""
import json
import base64
from helper import http


JPUSH_SEND_URL = 'https://api.jpush.cn/v3/push'
#JPUSH_SEND_URL = 'https://api.jpush.cn/v3/push/validate'
# APP_KEY = '0d3729ce7dee1e6c1b1eddf7'
# APP_SECRET = 'ad1c84134633e5f952a9e2e8'
# CHANNEL_SETTINGS = {
#     'pp': ('a2d027c7d96d7171e95e18be', 'ead151f0b066fd79b4112f8a', True),
#     'kaima': ('6cb4849b445f3fbc7b99b5cf', '460d69ec0ca7586e4b3a08b9', True),
#     'appstore': ('8290edf00cc0c3ca46b6cd73', '1e14c6e513ee2bcc8285588e', False),
# }


def send_notification(content, audience=None, tag=None, tag_and=None, alias=None, registration_id=None,
                      platform='all', time_to_live=3600, channels=None):
    """推送消息
    Args:
        content: 消息主体， 最长255字节，中文不超过80个
        audience: 推送设备对象 默认all, 其它： 别名(alias)、标签(tag)、注册ID(registration_id)、分群(tag_and)、广播(all)
            audience = {
                'tag': [...],              #并集标签列表， 最多20个
                'tag_and': [...],          # 交集标签列表 最多20个
                'alias': [...],            # 别名列表， 最多1000个
                'registration_id': [...],  # ID列表  最多1000个
            }
        tag:     标签， 并集标签列表， 最多20个  可以为all
        tag_and: 标签， 交集标签列表 最多20个
        alias:   别名列表， 最多1000个          可以为all
        registration_id: 注册ID列表  最多1000个   可以为all
        platform: 系统标识 默认all,  其它： ['android', 'ios', 'winphone]
        time_to_live: 存活时间，秒数, 最长不超过10天
    Returns:
        {'sendno': 推送序号，原样返回，
         'msg_id': 此条消息的标识
        }
    """
    try:
        from settings import PUSH_NOTIFICATION
    except ImportError:
        PUSH_NOTIFICATION = None

    if not PUSH_NOTIFICATION:
        raise Exception('No PUSH_NOTIFICATION, push abort!!')

    if audience is None:
        audience = {}
        if alias:
            audience['alias'] = alias
        elif registration_id:
            audience['registration_id'] = registration_id
        else:
            if tag:
                audience['tag'] = tag
            if tag_and:
                audience['tag_and'] = tag
    # 广播给所有人
    if not audience:
        audience = 'all'

    result = {}
    channels = channels or PUSH_NOTIFICATION.keys()
    for channel in channels:
        app_key, app_secret, apns_production = PUSH_NOTIFICATION[channel]
        data = _send_notification(app_key, app_secret, content, audience, platform, time_to_live, apns_production)
        result[channel] = data

    return result


def _send_notification(app_key, app_secret, content, audience='all',
                       platform='all', time_to_live=3600, apns_production=True):
    """推送消息
    Args:
        content: 消息主体， 最长255字节，中文不超过80个
        audience: 推送设备对象 默认all, 其它： 别名(alias)、标签(tag)、注册ID(registration_id)、分群(tag_and)、广播(all)
            audience = {
                'tag': [...],              #并集标签列表， 最多20个
                'tag_and': [...],          # 交集标签列表 最多20个
                'alias': [...],            # 别名列表， 最多1000个
                'registration_id': [...],  # ID列表  最多1000个
            }
        tag:     标签， 并集标签列表， 最多20个  可以为all
        tag_and: 标签， 交集标签列表 最多20个
        alias:   别名列表， 最多1000个          可以为all
        registration_id: 注册ID列表  最多1000个   可以为all
        platform: 系统标识 默认all,  其它： ['android', 'ios', 'winphone]
        time_to_live: 存活时间，秒数, 最长不超过10天
    Returns:
        {'sendno': 推送序号，原样返回，
         'msg_id': 此条消息的标识
        }
    """
    notification = {}
    if platform == 'all':
        notification['android'] = {'alert': content}
        notification['ios'] = {'alert': content, 'badge': 1,}
    elif 'android' in platform:
        notification['android'] = {'alert': content}
    elif 'ios' in platform:
        notification['ios'] = {'alert': content, 'badge': 1,}
    else:
        raise 'Error notification: %s' % locals()

    post_data = json.dumps({
        'platform': platform,
        'audience': audience,
        'notification' : notification,
        'options': {
            'time_to_live': time_to_live,
            'apns_production': apns_production,
        },
    })
    auth_key = '%s:%s' % (app_key, app_secret)
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Basic %s' % base64.b64encode(auth_key)}
    code, content = http.post(JPUSH_SEND_URL, post_data, headers)
    #print code, content
    if code != 200:
        return None
    # content = {"sendno":"0","msg_id":"301089823"}
    return json.loads(content)


if __name__ == '__main__':
    import time
    s = time.time()
    print send_notification('hello heros!')
    print time.time() - s
