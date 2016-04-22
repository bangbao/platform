# coding: utf-8

import re
from . import http


def get_mobile_attribution(mobile):
    """获取手机归属地
    """
    mobile = mobile[:11]
    url = 'http://tcc.taobao.com/cc/json/mobile_tel_segment.htm?tel={tel}'
    url = url.format(tel=mobile)

    _, result = http.get(url)
    result = result.decode('gb2312')
    match = re.search("province:'(?P<province>.*?)',", result)
    if match:
        province = match.group('province')
    else:
        province = None

    return {
        'province': province,      # 归属地省份
    }
