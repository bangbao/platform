# coding: utf-8

import re
import json
from . import http


def get_ipinfo_from_taobao(ip=None):
    """获取ip地址"""
    taobao = 'http://ip.taobao.com/service/getIpInfo2.php?ip={ip}'

    if ip is None:
        ip = 'myip'

    url = taobao.format(ip=ip)
    code, content = http.get(url)
    if code != 200:
        return None

    result = json.loads(content)
    if result['code'] != 0:
        return None

    ip = result['data']['ip']
    addr = u'{region}-{city}-{county}-{isp}'.format(**result['data'])
    print addr
    return {
        'ip': ip,
        'addr': addr,
    }


def get_ipinfo_from_ip138(ip=None):
    """获取ip地址"""
    if ip is None:
        ip138 = 'http://1212.ip138.com/ic.asp'
    else:
        ip138 = 'http://www.ip138.com/ips1388.asp?ip={ip}&action=2'.format(ip=ip)

    code, content = http.get(ip138)
    if code != 200:
        return None

    content = content.decode('gb2312')
    ip_search = re.search('\[?(?P<ip>\d+\.\d+\.\d+\.\d+)\]?', content)
    if ip_search is None:
        return None

    addr_search = re.search('<ul class=\"ul1\"><li>(?P<addr>[\s|\S]*?)<\/li><\/ul>', content)
    ip = ip_search.group('ip')
    addr = addr_search.group('addr')
    print addr
    # print repr(ip), addr.decode('gb2312')
    return {
        'ip': ip,
        'addr': addr,
    }


def get_ipinfo_from_baidu(ip):
    """获取ip地址
    """
    url = 'http://apis.baidu.com/apistore/iplookupservice/iplookup?ip={}'
    url = url.format(ip)

    headers = {'apikey': ''}

    code, content = http.get(url, headers=headers)
    # print code, content
    if code != 200:
        return None

    result = json.loads(content)
    return result


if __name__ == '__main__':
    ip = '36.110.30.93'
    print get_ipinfo_from_taobao(ip)
    print get_ipinfo_from_ip138(ip)
    print get_ipinfo_from_baidu(ip)
