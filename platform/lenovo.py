# coding: utf-8

import json
import urllib
from helper import http
from helper import utils

__VERSION__ = 'v1.9'
PLATFORM_NAME = 'lenovo'
APP_ID = '11111111111111111.app.ln'
APP_KEY = """-----BEGIN PRIVATE KEY-----
MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBAIPekh+ysORcZDTW
IT9Qcu+i+1+RJb4TY88ad/dQgPYhjbpUnmpeygOz4b+obDtWBFdzmE/B8WyK1YGR
3myJXOVS4N0YxaG7nweGymJOUSo5Aq1wJgIcMTmATxW0ticP6pOU6Ukn67FWcVc5
Rx4RvHGxmeapnddQx4kfhM8ksEDxAgMBAAECgYBwBY4KYWkFxTrW66R4vaW1zrVO
HOZ8Dsq1751Dud6juCNGy4V7hSSFerTmdHPlABBWHfugnXeypknzdPAHMbV4TL4s
VGPryzaFtIns/OQ4frjOhZgU95DNyv8NAZOHu+DBeEsVpD4LDXtTC5+vbyvH/cMz
RoDsbxynrX0sztqSVQJBAP/Xd1/HoJiHXAhUgi2F9A0vrgOx5zPJQnT2AV+O9o/P
rBoCVdiMR7pG0qeiiYuFANzWbZr8HooDETSUer2QoMMCQQCD83aWJl80FhRLB8f0
rnmlh7Mmb/bNw8XJ2c27fD4N5AphfCMmJ7ncgz5q9XRWRPH1Hb3Uk9lcE+jFy2ij
xLw7AkAbhogOYwDxSCbrsoPq9+2A+a9EMIDKfo3K3ajaKhx27oX6qmOoD7er3/DM
Hl2kCCRGnj9enF+Aw8G3IX5vJL9XAkAylhL/i2RyToinHyuMZZtjV3vaH5CJ4CUi
tmqGFyKfJq7IItRC23YI0RQL42Afdr0gEK/nIGtzPnq94baTGmhjAkEA0QHVwARZ
7KRX+B+Pr0X9cc9pWJtbhRhC+AcFRCPvEDY1IHYbF8DrQi6CQ/IhTCY8QDUcqT+8
tFu5JXFzbkSSCw==
-----END PRIVATE KEY-----"""
VERIFY_TOKEN_URL = 'http://passport.lenovo.com/interserver/authen/1.2/getaccountid'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'SUCCESS',
    1: 'FAILURE',
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
        }
    lpsust = params['session_id']

    query_data = urllib.urlencode({
        'lpsust': lpsust,
        'realm': APP_ID,
    })
    url = '%s?%s' % (VERIFY_TOKEN_URL, query_data)
    http_code, content = http.get(url)
    # 忽略http 406错误
    # print http_code, content
    obj = utils.xml2dict(content)
    openid = obj.get('AccountID')
    if not openid:
        return None

    return {
        'openid': openid,                # 平台用户ID
        'openname': obj['Username'],     # 平台用户名字
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        req: request封装，以下是验证所需参数
            sign: 签名
            transdata: 票据，JSON格式
                exorderno: 外部订单号  商户生成的订单号
                transid:   交易流水号  计费支付平台的交易流水号
                appid:     游戏 id  平台为商户应用分配的唯一代码
                waresid:   商品编码 商品编号,目前默认为 1
                feetype:   计费方式 计费类型:0–消费型_应用传入价格
                money:     交易金额  本次交易的金额,单位:分
                count:     购买数量 本次购买的商品数量
                result:    交易结果 交易结果:0–交易成功;1–交易失败
                transtype: 交易类型 交易类型:0 – 交易;1 – 冲正
                transtime: 交易时间 交易时间格式: yyyy-mm-dd hh24:mi:ss
                cpprivate: 商户私有信息
                paytype:   支付方式
        params: 测试专用
    """
    if not params:
        params = {
            'sign': req.get_argument('sign', ''),
            'transdata': req.get_argument('transdata', ''),
        }
    sign = utils.force_str(params['sign'])
    transdata = utils.force_str(params['transdata'])

    if not sign or not transdata:
        return RETURN_DATA, None

    data = json.loads(transdata)
    # 按接受成功处理
    if int(data['result']) != 0:
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    new_sign = utils.rsa_private_sign(APP_KEY, transdata)
    if new_sign != sign:
        return RETURN_DATA, None

    pay_data = {
        'app_order_id': data['exorderno'],                # 自定义定单id
        'order_id': data['transid'],                      # 平台定单id
        'order_money': float(data['money']) / 100,        # 平台实际支付money 单位元
        'uin': '',                                        # 平台用户id
        'platform': PLATFORM_NAME,                        # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    lpsust = 'ZAgAAAAAAAGE9MTAwMjQwMTczNTImYj0yJmM9NCZkPTExNzA1JmU9QkQ5Njk5MjkwODE5NjNERDM4REQzNzVFNUVBNDFDNzUxJmg9MTM5ODA0ODE5NTM5MyZpPTQzMjAwJmo9MCZvPTk4JTNBMEMlM0E4MiUzQUNFJTNBRDAlM0FFNCZwPW1hYyZxPTAmdXNlcm5hbWU9MTM0MzY2NjEzMTAyd1TV_eTJHylTF4UrQYv9'
    print login_verify('', params={'session_id': lpsust})
    transdata = '{"exorderno":"10004200000001100042","transid":"02113013118562300203","waresid":1,"appid":"20004600000001200046","feetype":0,"money":3000,"count":1,"result":0,"transtype":0,"transtime":"2013-01-31 18:57:27","cpprivate":"123456"}'
    key = 'MjhERTEwQkFBRDJBRTRERDhDM0FBNkZBMzNFQ0RFMTFCQTBCQzE3QU1UUTRPRFV6TkRjeU16UTVNRFUyTnpnek9ETXJNVE15T1RRME9EZzROVGsyTVRreU1ETXdNRE0zTnpjd01EazNNekV5T1RJek1qUXlNemN4';
    sign = '28adee792782d2f723e17ee1ef877e7 166bc3119507f43b06977786376c0434 633cabdb9ee80044bc8108d2e9b3c86e';
    #print payment_verify({'sign': sign, 'transdata': transdata, 'key': key})
    #print parse_key(APP_KEY)

