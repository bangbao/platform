# coding: utf-8

import utils
import json
import urllib
import time
import binascii
import hashlib
import hmac

PLATFORM_QQ_QZONE_APP_ID = '1111111'
PLATFORM_QQ_QZONE_APP_KEY = 'aaaaaaaa'
PLATFORM_QQ_QZONE_USER_INFO_URI = '/user/get_user_info'
PLATFORM_QQ_QZONE_BUY_GOODS_URI = '/mpay/buy_goods_m'
PLATFORM_QQ_QZONE_HOST = 'https://openapi.tencentyun.com'
PLATFORM_QQ_QZONE_SANDBOX_HOST = 'http://119.147.19.43'


def mk_soucrce(method, url_path, params, call_back=False):
    #这样是不会排序的
    #list_parms = map(lambda it: '%s=%s' % (it[0], str(it[1])), params.items())
    keys = params.keys()
    keys.sort()
    if call_back:
        list_parms = map(lambda it: '%s=%s' % (it, transcoding(str(params[it]))), keys)
    else:
        list_parms = map(lambda it: '%s=%s' % (it, str(params[it])), keys)
    str_params = urllib.quote('&'.join(list_parms),'')

    source = '%s&%s&%s' % (
        method.upper(),
        urllib.quote(url_path,''),
        str_params
    )

    return source


def hmac_sha1_sig(method, url_path, params, secret, call_back=False):
    source = mk_soucrce(method, url_path, params, call_back=call_back)
    hashed = hmac.new(secret, source, hashlib.sha1)
    return binascii.b2a_base64(hashed.digest())[:-1]


def transcoding(str_params):
    """除了 0~9 a~z A~Z !*() 之外其他字符按其ASCII码的十六进制加%进行表示，例如“-”编码为“%2D”。
    """
    character_set = set(r'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!*()')
    if set(str_params) - character_set:
        transcode_str = list(str_params)
        for k,v in enumerate(transcode_str):
            if v not in character_set:
                transcode_str[k] = "%%%s"%binascii.b2a_hex(v).upper()
        return ''.join(transcode_str)
    return str_params


class PLATFORM_QQ_QZONE(object):
    def __init__(self, debug=True):
        self.secret = '%s&' % PLATFORM_QQ_QZONE_APP_KEY
        if debug:
            self._host = PLATFORM_QQ_QZONE_SANDBOX_HOST
        else:
            self._host = PLATFORM_QQ_QZONE_HOST

    def analyze_data(self, data):
        """ 解析数据
        @param data: code=9094&msg=%5B0x733%5Dvalidate_access_token_fail
        @return: {'code': 909, 'msg': '[0x733]validate_access_token_fail'}
        """
        json_data = {}
        list_data = data.split('&')
        for i in list_data:
            k, v = i.split('=')
            json_data[k] = urllib.unquote(v)
        return json_data

    def generate_params(self, data, connector='&'):
        """
        """
        list_data = ['%s=%s' % (str(k), urllib.quote(str(v))) for k, v in data.iteritems()]
        return connector.join(list_data)

    def get_url(self, app_uri, params):
        """
        """
        return '%s?%s' % (app_uri, params)

    def check_user_info_open_api(self, params):
        """sid用户会话验证
        """
        params_data = {
            'openid': params.get('open_id'),
            'openkey': params.get('access_token'),
            'appid': PLATFORM_QQ_QZONE_APP_ID,
            'pf': params.get('pf'),
        }

        params_data['sig'] = hmac_sha1_sig('get', PLATFORM_QQ_QZONE_USER_INFO_URI, params_data, self.secret)
        params = self.generate_params(params_data)
        url = self.get_url('%s%s' % (self._host, PLATFORM_QQ_QZONE_USER_INFO_URI), params)
        http_code, content = utils.http.get(url, timeout=10, verify_certificate=False)

        if http_code != 200:
            return None

        obj = json.loads(content)
        ret = obj.get('ret', None)

        if ret:
            return None

        return True

    def buy_goods(self, open_id, openkey, pay_token, payitem, goodsmeta, goodsurl, pf, pfkey, app_metadata):
        """购买物品返回给前端
        Args:
            open_id: 从手Q登录态中获取的openid的值
            openkey: 从手Q登录态中获取的access_token 的值
            pay_token: 从手Q登录态中获取的pay_token的值
            payitem: 请使用x*p*num的格式，
                x表示物品ID，p表示单价（以Q点为单位，1Q币=10Q点，单价的制定需遵循腾讯定价规范），
                num表示默认的购买数量。（格式：物品ID1*单价1*建议数量1，批量购买物品时使用;分隔，
                如：id1*price1*num1;id2*price2*num2)长度必须<=512
            goodsmeta: 物品信息，格式必须是“name*des”，批量购买套餐时也只能有1个道具名称和1个描述，
                即给出该套餐的名称和描述。name表示物品的名称，des表示物品的描述信息。
                用户购买物品的确认支付页面，将显示该物品信息。
                长度必须<=256字符，必须使用utf8编码。
                目前goodsmeta超过76个字符后不能添加回车字符。
            goodsurl: 物品的图片url(长度<512字符)
            pf: 平台来源，$平台-$渠道-$版本-$业务标识。例如： openmobile_android-2001-android-xxxx
            pfkey: 跟平台来源和openkey根据规则生成的一个密钥串。如果是腾讯自研应用固定传递pfkey=”pfkey”
            app_metadata: （可选）发货时透传给应用。长度必须<=128字符
        """
        data = {
            'openid': open_id,
            'openkey': openkey,
            'pay_token': pay_token,
            'appid': PLATFORM_QQ_QZONE_APP_ID,
            'ts': int(time.time()),
            'payitem': payitem,
            'goodsmeta': goodsmeta,
            'goodsurl': goodsurl,
            'pf': '%s-100-android-100' % pf,  # 暂时填写pf需要和腾讯确认填写什么
            'pfkey': 'pfkey',
            'zoneid': 1,
            'appmode': 1,
            'app_metadata': app_metadata,
        }

        data['sig'] = hmac_sha1_sig('get', PLATFORM_QQ_QZONE_BUY_GOODS_URI, data, self.secret)
        cookie = {
            'session_id': open_id,  # openid
            'session_type': 'kp_actoken',  # kp_actoken
            'org_loc': 'mpay/buy_goods_m',  # 固定值
            'appip': PLATFORM_QQ_QZONE_APP_ID,    # appid
        }

        headers = {'Cookie': self.generate_params(cookie, connector=';')}
        params = self.generate_params(data)
        url = self.get_url('%s%s' % (self._host, PLATFORM_QQ_QZONE_BUY_GOODS_URI), params)
        http_code, content = utils.http.get(url, headers=headers, timeout=5, verify_certificate=False)

        if http_code != 200:
            return False

        obj = json.loads(content)
        if obj.get('ret') != 0:
            return False

        return obj

    def pay_callback_verify(self, body):
        """
        """
        openid = body.get('openid')
        token = body.get('token')
        sig = body.pop('sig', None)
        ts = body.get('ts', 0)

        if not openid or not token or not sig:
            return {'ret': 1, 'msg': 'params is null'}

        now_ts = int(time.time())
        if abs(now_ts - int(ts)) > 15 * 60:
            return {'ret': 2, 'msg': 'token expired'}

        generate_sig = hmac_sha1_sig('get', '/api/payment-callback-qzone/', body, self.secret, call_back=True)

        if sig != generate_sig:
            return {'ret': 4, 'msg': 'sig check error'}

        return {'ret': 0, 'msg': 'OK'}


