# coding: utf-8

import re
from . import http


def get_mobile_attribution(mobile):
    """获取手机归属地
    """
    mobile_re = re.compile('((^(13\d|14[57]|15[^4,\D]|17[345678]|18\d)'
                           '\d{8}|170[059]\d{7})(|\+\d))$')
    if not mobile_re.match(mobile):
        return {'province': None}

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
