#! /usr/bin/env python3
#coding:utf8
#导入smtplib和MIMEText
import smtplib
from email.mime.text import MIMEText
import sys
import time
import socket
'''
发送邮件，需带两个参数（主题、正文）
'''


def send_mail(to_list, sub, content):
    '''
    to_list:发给谁
    sub:主题
    content:内容
    send_mail("aaa@163.com","sub","content")
    '''
    mail_host = "smtp.yeah.net"
    mail_user = "xyliurui"  # 用户名
    mail_user_name = "pxeCtrlSys"  # 发件人姓名
    mail_pass = "lr99@ts.com"  # 密码
    mail_postfix = "yeah.net"

    me = mail_user_name + "<" + mail_user + "@" + mail_postfix + ">"
    # msg = MIMEText(content)  # 发送文本
    msg = MIMEText(content, 'html', 'utf-8')  # 发送html
    msg['Subject'] = sub
    msg['From'] = me
    # msg['To'] = ";".join(to_list)
    msg['To'] = to_list

    s = smtplib.SMTP(timeout=1000)
    s.set_debuglevel(1)
    s.connect(mail_host)
    s.login(mail_user, mail_pass)
    try:
        s.sendmail(me, to_list, msg.as_string())

        date = time.strftime("%Y-%m-%d %H:%M:%S")
        send_info = " 主题：" + sub + " 内容：" + content + " => " + to_list + "\n"
        send_mail_log = date + send_info
        file = open("Mail.log", "a", encoding="utf-8")
        file.write(send_mail_log)
        file.close()
        return True
    except Exception as e:
        print(str(e))
        return False
    finally:
        s.quit()


if __name__ == '__main__':
    msg = '''
        <html>
            <body>
            <h1>***欢迎使用PXE控制系统***</h1>
            <h2>【lr】您的验证码是：9999</h2>
            <p>网站地址：<a href="http://192.168.96.28/manage/select_default_image_control.html">点击跳转</a></p>
            </body>
        </html>'''
    print(send_mail("xyliurui@foxmail.com", "验证码：PXE控制系统注册", msg))
