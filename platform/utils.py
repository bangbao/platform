# coding: utf-8

import base64
import hashlib
import requests as http
import xml.sax.handler
from M2Crypto import RSA, EVP, BIO


def rsa_public_encrypt(public_key, message):
    """RSA方式公钥加密数据
    Args:
        public_key: 公钥
        message: 要加密的数据
    Returns:
        加密后的数据
    """
    bio = BIO.MemoryBuffer(public_key)
    rsa = RSA.load_pub_key_bio(bio)
    m = rsa.public_encrypt(str(message), RSA.pkcs1_padding)
    return base64.encodestring(m)


def rsa_public_decrypt(public_key, sign_data):
    """rsa方式公钥解密数据
    Args:
        public_key: 公钥
        sign_data: 要解密的数据
    Returns:
        加密后的数据
    """
    bio = BIO.MemoryBuffer(public_key)
    rsa = RSA.load_pub_key_bio(bio)
    b64string = base64.b64decode(sign_data)

    return rsa.public_decrypt(b64string, RSA.pkcs1_padding)


def rsa_verify_signature(publicKey, signedData, signature):
    """rsa方式验证数据签名
    Args:
        publicKey: 公钥， 已格式化的pem
        signedData: 要验证的数据
        signature: 签名
    Returns:
        布尔值，True表示验证通过，False表示验证失败
    """
    bio = BIO.MemoryBuffer(publicKey)
    rsa = RSA.load_pub_key_bio(bio)
    key = EVP.PKey()
    key.assign_rsa(rsa)
    key.verify_init()
    key.verify_update(signedData)
    return key.verify_final(b64decode(signature)) == 1


def rsa_verify_signature2(publicKey, signedData, signature):
    """rsa方式验证数据签名
    Args:
        publicKey: 公钥， 已格式化的pem
        signedData: 要验证的数据
        signature: 签名
    Returns:
        布尔值，True表示验证通过，False表示验证失败
    """
    bio = BIO.MemoryBuffer(publicKey)
    rsa = RSA.load_pub_key_bio(bio)
    m = EVP.MessageDigest('sha1')
    m.update(signedData)
    digest = m.final()
    return rsa.verify(digest, base64.decodestring(signature), "sha1")


def parse_cgi_data(cgi_data):
    """把cgi格式的数据转换为key-value格式
    Args:
        cgi_data: 数据 ‘sign=3&text=abc&bat=test'
    Yield:
        (key, value)
    """
    pairs = (s1 for s1 in sgi_data.split('&'))

    for name_value in pairs:
        nv = name_value.split('=', 1)
        if len(nv) != 2:
            continue
        yield nv


def pem_format(key):
    """格式ggplay公共key
    Args:
        key: google play publickey
    Returns:
        格式化后的publickey
    """
    def chunks(s, n):
        for start in range(0, len(s), n):
            yield s[start:start + n]

    return '\n'.join([
        '-----BEGIN PUBLIC KEY-----',
        '\n'.join(chunks(key, 64)),
        '-----END PUBLIC KEY-----'
    ])


def xml2dict(xml_data):
    """解析支付定单数据xml到字典格式
    Args:
        xml_data: xml数据
    Returns:
        字典格式数据
    """
    if isinstance(xml_data, unicode):
        xml_data = xml_data.encode('utf-8')

    xh = XMLHandler()
    xml.sax.parseString(xml_data, xh)

    return xh.getDict()


class XMLHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.buffer = ""
        self.mapping = {}

    def startElement(self, name, attributes):
        self.buffer = ""

    def characters(self, data):
        self.buffer += data

    def endElement(self, name):
        self.mapping[name] = self.buffer

    def getDict(self):
        return self.mapping

