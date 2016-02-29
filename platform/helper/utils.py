# coding: utf-8

import hmac
import base64
import hashlib
import xml.sax.handler
from M2Crypto import RSA, EVP, BIO


def force_str(text, encoding="utf-8", errors='strict'):
    """强制str编码
    """
    t_type = type(text)
    if t_type == str:
        return text
    elif t_type == unicode:
        return text.encode(encoding, errors)
    return str(text)


def force_unicode(text, encoding="utf-8", errors='strict'):
    """强制用unicode
    """
    t_type = type(text)
    if t_type == str:
        return text.decode(encoding, errors)
    elif t_type == unicode:
        return text
    elif hasattr(text, '__unicode__'):
        return unicode(text)
    return unicode(str(text), encoding, errors)


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


def rsa_public_decrypt(public_key, sign_data, max_decrypt_block=0):
    """rsa方式公钥解密数据
    Args:
        public_key: 公钥
        sign_data: 要解密的数据
        max_decrypt_block: 是否需分段解密 0：无需分段解密；正整数：为分段解密块长度
    Returns:
        解密后的数据
    """
    bio = BIO.MemoryBuffer(public_key)
    rsa = RSA.load_pub_key_bio(bio)
    b64string = base64.b64decode(sign_data)

    if max_decrypt_block:
        data = ''
        while b64string:
            _data = b64string[:max_decrypt_block]
            b64string = b64string[max_decrypt_block:]
            data += rsa.public_decrypt(_data, RSA.pkcs1_padding)
        return data
    return rsa.public_decrypt(b64string, RSA.pkcs1_padding)


def rsa_private_decrypt(private_key, sign_data, max_decrypt_block=0):
    """rsa方式私钥解密数据
    Args:
        private_key: 私钥
        sign_data: 要解密的数据
        max_decrypt_block: 是否需分段解密 0：无需分段解密；正整数：为分段解密块长度
    Returns:
        解密后的数据
    """
    bio = BIO.MemoryBuffer(private_key)
    rsa = RSA.load_pub_key_bio(bio)
    b64string = base64.b64decode(sign_data)

    if max_decrypt_block:
        data = ''
        while b64string:
            _data = b64string[:max_decrypt_block]
            b64string = b64string[max_decrypt_block:]
            data += rsa.private_decrypt(_data, RSA.pkcs1_padding)
        return data
    return rsa.private_decrypt(b64string, RSA.pkcs1_padding)


def rsa_private_sign(private_key, message, algo='sha1'):
    """RSA方式私钥签名数据
    Args:
        private_key: 私钥
        message: 要签名的数据
        algo: The method that created the digest, only in `md5` or `sha1`
    Returns:
        签名
    """
    bio = BIO.MemoryBuffer(private_key)
    rsa = RSA.load_key_bio(bio)
    if algo == 'md5':
        digest = hashlib.md5(message).digest()
    else:
        digest = hashlib.sha1(message).digest()
    m = rsa.sign(digest, algo=algo)
    #m = rsa.private_encrypt(message, RSA.pkcs1_padding)

    return base64.b64encode(m)


def rsa_verify_signature(publicKey, signedData, signature, md='sha1'):
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
    key.assign_rsa(rsa, capture=0)
    key.reset_context(md=md)
    key.verify_init()
    key.verify_update(signedData)
    return key.verify_final(base64.b64decode(signature)) == 1


def aes_decrypt(key, text):
    """aes方式解密数据
    Args:
        aes_key: 加密用的key
        text: 要解密的串
    Returns:
        daes方式解密后数据
    """
    data = base64.b64decode(text)
    cipher = EVP.Cipher(alg='aes_128_ecb', key=key, op=0, d='sha1', iv='\0'*16)
    buf = cipher.update(data)
    buf += cipher.final()

    return buf


def des3_encrypt(key, text):
    """des3方式加密数据
    Args:
        key: 加密用的key
        text: 要加密的串
    Returns:
        des3方式加密后数据
    """
    cipher = EVP.Cipher(alg='des_ede3_ecb', key=key, op=1, iv='\0'*16)

    encrypted_text = cipher.update(text)
    encrypted_text += cipher.final()

    return encrypted_text


def des3_decrypt(key, text):
    """des3方式解密数据
    Args:
        key: 加密用的key
        text: 要解密的串
    Returns:
        des3方式解密后数据
    """
    decipher = EVP.Cipher(alg='des_ede3_ecb', key=key, op=0, iv='\0'*16)

    decrypted_text = decipher.update(text)
    decrypted_text += decipher.final()

    return decrypted_text


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


def parse_cgi_data(cgi_data):
    """把cgi格式的数据转换为key-value格式
    Args:
        cgi_data: 数据 ‘sign=3&text=abc&bat=test'
    Yield:
        (key, value)
    """
    pairs = (s1 for s1 in cgi_data.split('&'))

    for name_value in pairs:
        nv = name_value.split('=', 1)
        if len(nv) != 2:
            continue
        yield nv


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


def trans_key2pm(app_secret_key):
    """解析APP_KEY
    Args:
        app_secret_key: 原始的app_secret_key
    Returns:
        privateKey, modkey
    """
    decodeBaseStr = base64.b64decode(app_secret_key)
    real_key = base64.b64decode(decodeBaseStr[40:])
    privateKey, modkey = real_key.split('+')

    return int(privateKey), int(modkey)


def trans_sign2md5(sign, app_key):
    """从加密串中解析出md5签名
    Args:
        sign: 加密串： 28adee7e1ef877e7 166bc3376c0434 633c8d2e9b3c86e
        app_key: 解密用的key
    Returns:
        md5签名串
    """
    md5str_list = []
    p, m = trans_key2pm(app_key)

    for long_str in sign.split(' '):
        if long_str:
            v = int(long_str, 16)
            v = pow(v, p, m)
            byte = trans_int2byte(v)
            md5str_list.append(byte)

    md5str = ''.join(md5str_list)
    return md5str.strip()


def trans_int2byte(num, length=256):
    """把一个长整形转换成字节串
    Args:
        num: 长整数
    Returns:
        字节串
    """
    bits = []
    while num > 0:
        num, asc = divmod(num, length)
        bit = chr(asc)
        bits.append(bit)

    reverse_bits = reversed(bits)
    return ''.join(reverse_bits)


def hmac_sha1_sign(key, data, hexdigest=True):
    """hmac_sha1算法签名
    Args:
        key: 签名密钥
        data: 要签名的数据
        hexdigest: 默认16进制
    Returns:
        签名后的16进制串
    """
    if isinstance(data, unicode):
        data = data.encode('utf-8')
    if hexdigest:
        return hmac.new(key, data, hashlib.sha1).hexdigest()
    else:
        return hmac.new(key, data, hashlib.sha1).digest()


def hashlib_md5_sign(sign_str):
    """hashlib_md5算法签名
    Args:
        sign_str: 要签名数据
    Returns:
        签名串
    """
    if isinstance(sign_str, unicode):
        sign_str = sign_str.encode('utf-8')
    return hashlib.md5(sign_str).hexdigest()


