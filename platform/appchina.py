# coding: utf-8

import json
import urllib
from helper import http
from helper import utils

# 应用汇平台
__VERSION__ = '4.0.3'
PLATFORM_NAME = 'appchina'
APP_ID = '111111'
APP_KEY = 'xxxxxxxxxxxxxxx'
PAY_APP_ID = '1111111111111'
PAY_APP_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxx'
# 验证用户ticket接口
GET_USERINFO_URL = 'http://api.appchina.com/appchina-usersdk/user/get.json'
# 返回数据0是成功的数据，1是失败的数据
RETURN_DATA = {
    0: 'SUCCESS',
    1: 'NOT SUCCESS',
}


def login_verify(req, params=None):
    """登录验证
    Args:
        req: request封装，以下是验证所需参数
            session_id: ticket
        params: 测试专用
    Returns:
        平台相关信息(openid必须有)
    """
    if not params:
        params = {
            'session_id': req.get_argument('session_id'),
        }
    ticket = params['session_id']

    query_data = urllib.urlencode({
        'ticket': ticket,
        'app_id': APP_ID,
        'app_key': APP_KEY,
    })
    http_code, content = http.post(GET_USERINFO_URL, query_data)
    # print http_code, content
    if http_code != 200:
        return None

    # {"data": {"nick_name": "jakyzhang", "user_name": null,"phone": null,
    #  "email": "jakyzhang@live.com","ticket": "0a987","user_id": 16058,
    #  "actived": true},"status": 0,"message": "OK"}
    obj = json.loads(content)
    if obj['status'] != 0:
        return None

    return {
        'openid': obj['data']['user_id'],          # 平台标识
        'openname': obj['data']['nick_name'],      # 平台昵称
    }


def payment_verify(req, params=None):
    """支付验证
    Args:
        params: 回调字典数据
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
    """
    if not params:
        params = {
            'sign': req.get_argument('sign', ''),
            'transdata': req.get_argument('transdata', ''),
        }
    sign, transdata = params['sign'], params['transdata']

    if not sign or not transdata:
        return RETURN_DATA, None

    s_md5 = utils.trans_sign2md5(sign, PAY_APP_KEY)
    t_md5 = utils.hashlib_md5_sign(transdata)
    if s_md5 != t_md5:
        return RETURN_DATA, None

    data = json.loads(transdata)
    if int(data['result']) != 0:
        return_data = dict(RETURN_DATA)
        return_data[1] = RETURN_DATA[0]
        return return_data, None

    pay_data = {
        'app_order_id': data['exorderno'],                # 自定义定单id
        'order_id': data['transid'],                      # 平台定单id
        'order_money': float(data['money']) / 100,        # 平台实际支付money 单位元
        'uin': '',                                        # 平台用户id
        'platform': PLATFORM_NAME,                        # 平台标识名
    }
    return RETURN_DATA, pay_data


if __name__ == '__main__':
    params = {'session_id': '10004200000001100042'}
    print login_verify('', params)
    transdata = '{"exorderno":"10004200000001100042","transid":"02113013118562300203","waresid":1,"appid":"20004600000001200046","feetype":0,"money":3000,"count":1,"result":0,"transtype":0,"transtime":"2013-01-31 18:57:27","cpprivate":"123456"}'
    key = 'MjhERTEwQkFBRDJBRTRERDhDM0FBNkZBMzNFQ0RFMTFCQTBCQzE3QU1UUTRPRFV6TkRjeU16UTVNRFUyTnpnek9ETXJNVE15T1RRME9EZzROVGsyTVRreU1ETXdNRE0zTnpjd01EazNNekV5T1RJek1qUXlNemN4';
    sign = '28adee792782d2f723e17ee1ef877e7 166bc3119507f43b06977786376c0434 633cabdb9ee80044bc8108d2e9b3c86e';
    #print payment_verify({'sign': sign, 'transdata': transdata, 'key': key})




