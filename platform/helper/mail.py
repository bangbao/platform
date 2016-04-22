# coding: utf-8

import os
import smtplib
import mimetypes
from email import MIMEBase
from email import MIMEText
from email import MIMEMultipart
from email import header


def send_mail(subject, message, to_addrs, attachments=None, auth_kwargs=None):
    """发送邮件
    Args:
        subject: 邮件标题
        message: 邮件主题
        to_addrs: 接受邮件列表
        attachments: 附件文件列表, 可为None
        auth_kwargs: 发送者数据, 可为None
    """
    auth_kwargs = auth_kwargs or {}
    SMTP_HOST = auth_kwargs.get('SMTP_HOST', "smtp.exmail.qq.com")
    AUTH_USER = auth_kwargs.get('AUTH_USER', "xxxxxxxx@qq.com")
    AUTH_PASS = auth_kwargs.get('AUTH_PASS', "xxxxxxxxx")
    FROM_ADDR = AUTH_USER

    subject = header.Header(subject, 'utf-8')
    # 构造MIMEText对象做为邮件显示内容并附加到根容器
    message = MIMEText.MIMEText(message, _charset="utf-8")
    # 构造MIMEMultipart对象做为根容器
    email = MIMEMultipart.MIMEMultipart()
    email.attach(message)

    attachments = attachments or []
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
            email.attach(attach)

    # 设置根容器属性
    email['From'] = FROM_ADDR
    email['To'] = ';'.join(to_addrs) if to_addrs else None
    email['Subject'] = subject
    # 得到格式化后的完整文本
    fullText = email.as_string()

    # 用smtp发送邮件
    smtp = smtplib.SMTP(SMTP_HOST)
    smtp.login(AUTH_USER, AUTH_PASS)
    smtp.sendmail(FROM_ADDR, to_addrs, fullText)
    smtp.quit()
