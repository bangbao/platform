
import json
import urllib
from helper import http
from helper import utils

PLATFORM_NAME = 'lewan'
APP_ID = '11111'
PAY_KEY = 'xxxxxxxxxxxxxxxxxxxxxx'
GET_USERINFO_URL = 'http://www.lewanduo.com/mobile/user/verifyToken.html'
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+GY2/8wJuINxzJo9uWoMRUDcx
ONuK/48Fikze8EFpKWLLr6mBpqeoDVvZQoqGhGKn5wdtHujiCUYSn6pcWKY2Fz2R
xw6/1uA1gzKcLE36KLUkqvFbA3gItSiO3ADNCwJ1ochhdfcEnH2dtbiv5+f7m+xv
5B1aEP142v2CtYKFFQIDAQAB
-----END PUBLIC KEY-----"""
PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBAIX/cV2vLpxqBEFm
uPpH+c+kLUCYihy2rWbKFSi4RmsRp9adEevTju7EeGWLLLPibz3RAnwCBmeMTAIl
A/ltfIDdNMYN4dZEuZ+m+AlprXeS53hP7f8ie9iA//r4aOzhtbwU+wecYuw++JBV
85eUNbVrkALBnkDazjlWnv0A+EfFAgMBAAECgYBHUGbGRFibODUhlYj28t1569eF
nGlM1NA+d2iBbmlTzGa16oxCJSrZ2kh1Sne1GNq5XIZk9zLvYxSEw6x00BdFNSTL
ufvMhhCGvdhevdhC828UZ7vgehArZv78FSj0cSERoj5IfcCXfPlsMlj0agKKLeq5
xMHsSZEGdBkKA4e4IQJBAPSVsB5Zt4iiAx5Qun2QwtdYc0aO4sxk3cchI6H9RJqX
59Cm2BpN68tDhssODoc53u2/cjuc38W4H9lbC2jOq0kCQQCMQHTWztG8QNq8FOv7
bDItUNqbfqeuH847WLkVGsjX33VewnOEZLdO4J5xpacXmsT7p2QwOMGytAbh43aM
U1ydAkAwmSWbgjwjm/1+oo/Lr13nqB2PoYiTEF+4127bGxXsmc5n+R7raxw1ET/R
TQO5/te66dVq3urfwIwjhiGoO5hxAkBvkIZgqTwlZ+GXY30kDrkLWxnKP0HbPOms
Q7NWmmvRbKvMqRmC4yr9z6e592+nUzIGjO0hfsR2BsbCwVH35gfxAkEAy3oNygRr
Y85yheqg45lJ5gYjB9cpq8qwluCbJepLUmqOWSYovX//JmK/W/sSDiWdqHN37d0J
frObNh0xxEMB5g==
-----END PRIVATE KEY-----"""
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'success',
    1: 'failure',
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
            'session_id': req.get_argument('session_id', ''),
            'user_id': req.get_argument('user_id', ''),
            'nickname': req.get_argument('nickname', ''),
            'channelId': req.get_argument('new_channel', ''),
        }
    token = params['session_id']
    code = params['user_id']
    password = params['nickname']
    channelId = params['channelId']

    query_data = urllib.quote(json.dumps({
        'code': code,
        'password': password,
        'token': token,
        'channelId': channelId,
        'app_id': APP_ID,
    }))
    url = '%s?notifyData=%s' % (GET_USERINFO_URL, query_data)
    try:
        # 对方服务器不稳定
        http_code, content = http.get(url)
    except:
        return None
    #print http_code, content
    if http_code != 200:
        return None

    obj = json.loads(content)
    # userId, code, app_id, success, msg
    if obj['success'] not in {'true', True}:
        return None

    #openid = obj['code']
    return {
        'openid': obj['userId'],          # 平台用户ID
        'openname': obj['code'],      # 平台用户名字
    }





def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            encryptkey: 使用 RSA 加密商户AESKey后生成的密钥密文
            data: 对含有签名的基本业务数据JSON串加密后形成的密文
        params: 测试专用
    """
    if not params:
        params = {
            'encryptkey': req.get_argument('encryptkey', ''),
            'data': req.get_argument('data', ''),
        }
    encryptkey = params['encryptkey']
    data = params['data']

    if not encryptkey or not data:
        return RETURN_DATA, None

    aes_key = utils.rsa_private_decrypt(PRIVATE_KEY, encryptkey)
    aes_data = utils.aes_decrypt(aes_key, data)
    aes_dict = json.loads(aes_data)

    sign = aes_dict.pop('sign')
    result = sorted(aes_dict.iteritems())

    result = ('%s' % v for k, v in result)
    result_str = ''.join(result)
    if isinstance(result_str, unicode):
        result_str = result_str.encode('utf-8')

    if not utils.rsa_verify_signature(PUBLIC_KEY, result_str, sign):
        return RETURN_DATA, None

    if aes_dict.get('payState', -1) != 2:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': aes_dict['gameOrderId'],                  # 自定义定单id
        'order_id': aes_dict['lewanOrderId'],                     # 平台定单id
        'order_money': float(aes_dict['paySuccessMoney']) / 100,  # 平台实际支付money 单位元
        'uin': '',                                                # 平台用户id
        'platform': PLATFORM_NAME,                                # 平台标识名
    }
    return RETURN_DATA, pay_data



def payment_verify(encryptkey, params):
    """支付回调验证，extern 为自定义
    Args:
        params: 字典参数数据
            gameId:      游戏ID
            gameOrderId:     订单号
            gameUserId: 用户标识
            payState: 支付状态
            errorCode:   错误码
            errorMsg:       错误信息
            expandMsg:         扩展信息
            paySuccessMoney:      支付金额
            lewanOrderId:        乐玩系统里的定单ID
            serverId:        服务的服ID
            balanceAmt:        支付余额
            sign:        签名
    Returns:
        支付数据
    """
    def generate_aes_key(PRIVATEKEY, encrypt_key):
        private_bio = BIO.MemoryBuffer(PRIVATEKEY)
        private_rsa = RSA.load_key_bio(private_bio)
        b64string = base64.b64decode(encrypt_key)
        aes_key = private_rsa.private_decrypt(b64string, RSA.pkcs1_padding)
        return aes_key
    aes_key = generate_aes_key(PRIVATEKEY, encryptkey)

    def generate_aes(base64_data, aes_key):
        data = base64.b64decode(base64_data)
        iv = '\0' * 16
        cipher = EVP.Cipher(alg='aes_128_ecb', key=aes_key, iv=iv, op=0, d='sha1')
        buf = cipher.update(data)
        buf = buf + cipher.final()
        del cipher
        return buf

    aes_data = generate_aes(params, aes_key)

    aes_dict = json.loads(aes_data)
    sign = aes_dict.pop('sign')
    result = sorted(aes_dict.iteritems(), key=lambda x: x[0])

    result = ['%s' % v for k, v in result]
    result_str = ''.join(result)

    if isinstance(result_str, unicode):
        result_str = result_str.encode('utf-8')

    if not utils.rsa_verify_signature(PUBLICKEY, result_str, sign):
        return None

    if aes_dict.get('payState', -1) not in {2}:
        return None

    return aes_dict



# if __name__ == '__main__':
#     encry = 'l4vpFR0Xq9GJTJJvfgvbVNWh741UM8TFIyh8CWDJjBTktVd0AmE4BqpXI+s3xcwvZl+UNRO+gcTqUiWj8qOUBHNynASKrYiAladt9F22S51S3mTe5xTiW5MfAd0SlXjVq7cD8Zo2XlS6pLC6XOzG4a+9LPS7kHTxlVRsYtgOeLg='
#     data = 'lDAMn2UBHunBwjqLOrJ4TPFPavixMv4H+CoLsZh7JIz31KQOCiiS/Mgwm32rMROl0hCARHBKzjjafxuMADwxDP1maligHu/cXq3VKPywPQjWUDVavLU9ZsJcsfA+vBg8ypRf20lLircirE3LZO76dBO0hMzVICtZaXDM8Cgh95+plE/Jv+9YOjypD0SLK7D1XX1jFXuCSZkz/lkVTraD96cKyX9yHhZJlFsIJo4gOfCRREsUfej3NykICd6qTTBI36LSQax8PjimH+86hnaAvM4lv7E4QNt0D7Ir5NBp1Sq4t4eKt0FmidqarkEvGH2PwrPNfKeW8Slg4CX0jIidaIvgg3c6lEPOrqcykW4364VpRa/IIrYNu5ggvcsAEEus8yckExqGzJnNAPHOt3G6njsMSOanNnJJRcQMNywB3V/feMQ1FcBDEqMHrKgThi9wh7meu+Uq4xglq4gJV/gQB8dW5hbpry1ux8Z5B8UrPjs='
#     print payment_verify(encry, data)

