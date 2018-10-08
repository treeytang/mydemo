from django.conf.urls import url,include
from .views import UserInfoView, UploadImageView, UpdatePwdView, SendEmailCodeView,MyMessageView, UpdateEmailView, MyCourseView,MyFavCourseView,MyFavOrgView,MyFavTeacherView

urlpatterns = [
    # 课程机构的首页
    url(r'^info/$', UserInfoView.as_view(), name='info'),
    #修改用户头像
    url(r'^upload/image/$', UploadImageView.as_view(), name='upload_image'),
    #用户个人中心修改密码
    url(r'^update/pwd/$', UpdatePwdView.as_view(), name='update_pwd'),

    #用户个人中心发送验证码
    url(r'^sendemail_code/$', SendEmailCodeView.as_view(), name='sendemail_code'),

    #用户修改邮箱
    url(r'^update_email/$', UpdateEmailView.as_view(), name='update_email'),

    #用户个人中心 我的课程
    url(r'^mycourse/$', MyCourseView.as_view(), name='mycourse'),

    #我的收藏机构
    url(r'^myfav_org/$', MyFavOrgView.as_view(), name='myfav_org'),

    #我的收藏讲师
    url(r'^myfav_teacher/$', MyFavTeacherView.as_view(), name='myfav_teacher'),

    #我的收藏课程
    url(r'^myfav_course/$', MyFavCourseView.as_view(), name='myfav_course'),

    #我的消息
    url(r'^mymessage/$', MyMessageView.as_view(), name='mymessage')

]