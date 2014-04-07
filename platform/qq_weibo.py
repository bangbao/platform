# coding: utf-8

# 腾讯微薄
PLATFORM_WEIBO_QQ_SERVICE_URL = 'http://open.t.qq.com/api/user/info'
PLATFORM_WEIBO_QQ_APP_KEY = '111111111'
PLATFORM_WEIBO_QQ_APP_SECRET = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
PLATFORM_WEIBO_QQ_OAUTH_VERSION = '2.a'
PLATFORM_WEIBO_QQ_SCOPE = 'all'
PLATFORM_WEIBO_QQ_FORMAT = 'json'


def login_verify(openid, access_token, clientip):
    """ 进行weibo_qq平台的信息验证
    """
    url_params = {
        'access_token': access_token,
        'openid': openid,
        'oauth_consumer_key': PLATFORM_WEIBO_QQ_APP_KEY,
        'oauth_version': PLATFORM_WEIBO_QQ_OAUTH_VERSION,
        'scope': PLATFORM_WEIBO_QQ_SCOPE,
        'format': PLATFORM_WEIBO_QQ_FORMAT,
        'clientip': clientip,
    }
    url = '%s?%s' % (PLATFORM_WEIBO_QQ_SERVICE_URL, urllib.urlencode(url_params))
    http_code, content = utils.http.get(url.encode('utf-8'), timeout=10)

    if http_code != 200:
        return None

    obj = json.loads(content)

    if obj['errcode'] != 0:
        return None

    return openid

