from random import Random
from users.models import EmailVerifyRecord
from django.core.mail import send_mail
from McOnline.settings import EMAIL_FORM


def send_register_email(email, send_type='register'):#参数为需要发送的邮箱和以什么的形式发送验证码（注册 找回密码）
    email_record = EmailVerifyRecord()#邮箱验证码
    if send_type == 'update_email':
        code = random_str(4)
    else:
        code = random_str(16)#验证码 随机字符串 长16
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()
    #定义邮件的内容 邮件的标题 正文
    email_title = ''
    email_body = ''

    if send_type == 'register':
        email_title = '慕学在线网注册激活链接'
        email_body = '请点击下面的链接激活你的账号：http://127.0.0.1:8000/active/{0}'.format(code)
        send_status = send_mail(email_title, email_body, EMAIL_FORM, [email])
        if send_status:
            pass

    elif send_type == 'forget':
        email_title = '慕学在线网密码重置链接'
        email_body = '请点击下面的链接重置密码：http://127.0.0.1:8000/reset/{0}'.format(code)
        send_status = send_mail(email_title, email_body, EMAIL_FORM, [email])
        if send_status:
            pass

    elif send_type == 'update_email':
        email_title = '慕学在线网修改邮箱'
        email_body = '慕学在线网修改邮箱验证码{0}'.format(code)
        send_status = send_mail(email_title, email_body, EMAIL_FORM, [email])
        if send_status:
            pass



def random_str(randomlenght=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlenght):
        str+=chars[random.randint(0, length)]#利用了随机索引的方式生成验证码
    return str
