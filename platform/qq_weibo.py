# coding: utf-8

# 腾讯微薄
PALTFORM_NAME = 'qq_weibo'
PLATFORM_QQ_WEIBO_SERVICE_URL = 'http://open.t.qq.com/api/user/info'
PLATFORM_QQ_WEIBO_APP_KEY = '111111111'
PLATFORM_QQ_WEIBO_APP_SECRET = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
PLATFORM_QQ_WEIBO_OAUTH_VERSION = '2.a'
PLATFORM_QQ_WEIBO_SCOPE = 'all'
PLATFORM_QQ_WEIBO_FORMAT = 'json'


def login_verify(openid, access_token, clientip):
    """ 进行weibo_qq平台的信息验证
    """
    url_params = {
        'access_token': access_token,
        'openid': openid,
        'oauth_consumer_key': PLATFORM_QQ_WEIBO_APP_KEY,
        'oauth_version': PLATFORM_QQ_WEIBO_OAUTH_VERSION,
        'scope': PLATFORM_QQ_WEIBO_SCOPE,
        'format': PLATFORM_QQ_WEIBO_FORMAT,
        'clientip': clientip,
    }
    url = '%s?%s' % (PLATFORM_QQ_WEIBO_SERVICE_URL, urllib.urlencode(url_params))
    http_code, content = utils.http.get(url.encode('utf-8'), timeout=10)

    if http_code != 200:
        return None

    obj = json.loads(content)

    if obj['errcode'] != 0:
        return None

    return openid

