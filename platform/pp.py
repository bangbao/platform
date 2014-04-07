# coding: utf-8

import utils

import socket
import struct
import json
import requests as http
from M2Crypto import RSA, EVP, BIO

PP_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
......
-----END PUBLIC KEY-----"""

SERVER = 'passport_i.25pp.com'
PORT = 8080


class PPSocket(object):
    _connection = None

    def __init__(self, server, port):
        self.connect(server, port)

    def connect(self, server, port):
        try:
            self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, e:
            print 'Strange error creating socket:%s' % e

        try:
            self._connection.connect((server, port))
        except socket.gaierror, e:
            print 'Address-related error connecting to server :%s' % e
        except socket.error, e:
            print 'Connection error:%s' % e

    def disconnect(self):
        if self._connection:
            self._connection.close()
            self._connection = None
            return True
        return False

    def write(self, data):
        try:
            self._connection.sendall(data)
        except socket.error, e:
            print 'sendall error:%s' % e

    def read(self):
        try:
            result = self._connection.recv(1024)
        except socket.error, e:
            print 'recv error:%s' % e
            result = ""
        return result


def login_verify(token_key):
    """
    Args:
        uin: pp uid
        token_key: 二进制数据
    """
    ppSocket = PPSocket(SERVER, PORT)
    length_cmd = struct.pack("<2I", len(token_key) + 8, 0xAA000022)
    send_data = [length_cmd, token_key]
    ppSocket.write(''.join(send_data))
    result_data = ppSocket.read()
    result_len = len(result_data)

    data = {'status': 0, 'uin': None}

    if result_len == 0:
        # 失败
        pass
    elif result_len == struct.calcsize("<3I"):
        # 失败
        ps_len, ps_commmand, ps_status = struct.unpack("<3I", result_data)
        data['status'] = ps_status
    else:
        # 成功
        username_len = result_len - (3 * 4 + 1 + 8)
        try:
            ps_len, ps_commmand, ps_status, ps_username, ps_end, ps_uid = struct.unpack("<3I%dssQ" % username_len, result_data)
        except:
            ps_status = 100
            ps_uid = None

        if ps_status == 0:
            data['status'] = 1
            data['uin'] = ps_uid

    self.disconnect()

    return data


def payment_verify(data):
    """data 为服务器回调的参数们
    """
    sign = data.get('sign', '')
    account = data.get('account', '')
    amount = data.get('amount', '0')
    app_id = data.get('app_id', '')
    billno = data.get('billno', '')
    order_id = data.get('order_id', '')
    status = int(data.get('status', 0))
    roleid = data.get('roleid', '')
    uuid = data.get('uuid', '')
    zone = data.get('zone', '')

    if status != 0:
        return False

    context = utils.rsa_public_decrypt(PP_PUBLIC_KEY, sign)
    order_sign = json.loads(context)

    for k, v in order_sign.iteritems():
        if v != data[k]:
            return False

    return order_sign


