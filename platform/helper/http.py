# coding: utf-8

import urllib2


def request(method, url, data=None, headers=None, timeout=2):
    """一个简单的http请求封装
    Args:
        url: string, URL to fetch
        method: HTTP method, e.g. "GET" or "POST"
        headers: Additional HTTP headers to pass on the request,
        data: HTTP body to pass on the request
    """
    headers = headers or {}
    request = urllib2.Request(url, data, headers)
    try:
        response = urllib2.urlopen(request, timeout=timeout)
        code, content = response.getcode(), response.read()
    # 非200状态会抛异常，只取返回状态码和返回数据
    except urllib2.HTTPError as e:
        code, content = e.code, e.fp.read()

    return code, content


def get(url, headers=None, timeout=2, validate_cert=False):
    return request('GET', url, headers=headers, timeout=timeout)


def post(url, data=None, headers=None, timeout=2, validate_cert=False):
    return request('POST', url, data, headers=headers, timeout=timeout)


