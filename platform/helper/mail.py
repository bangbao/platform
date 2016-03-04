# coding: utf-8

import os
import smtplib
import mimetypes
from email import MIMEBase
from email import MIMEText
from email import MIMEMultipart

def send_mail(subject='', message='', attachments=None,
              from_addr=None, to_addr=None, **smtp):
    """发送邮件
    """
    subject = MIMEText.MIMEText(subject, _charset="utf-8").as_string()
    # 构造MIMEText对象做为邮件显示内容并附加到根容器
    message = MIMEText.MIMEText(message, _charset="utf-8")
    # 构造MIMEMultipart对象做为根容器
    main_msg = MIMEMultipart.MIMEMultipart()
    main_msg.attach(message)

    if attachments is not None:
        for attachment_filename in attachments:
            with open(attachment_filename, 'rb') as f:
                basename = os.path.basename(attachment_filename)
                ctype, encoding = mimetypes.guess_type(attachment_filename)
                if ctype is None or encoding is not None:
                    ctype = 'application/octet-stream'
                maintype, subtype = ctype.split('/', 1)
                attach = MIMEBase.MIMEBase(maintype, subtype)
                attach.set_payload(f.read())
                attach.add_header('Content-Disposition', 'attachment',
                                  filename=basename)
                main_msg.attach(attach)

    # 设置根容器属性
    main_msg['From'] = from_addr
    main_msg['To'] = to_addr
    main_msg['Subject'] = subject
    # 得到格式化后的完整文本
    fullText = main_msg.as_string()
    # 用smtp发送邮件
    try:
        server = smtplib.SMTP()
        server.login('', '')
        server.sendmail(from_addr, to_addr, fullText)
    finally:
        server.quit()


if __name__ == '__main__':
    send_mail()


