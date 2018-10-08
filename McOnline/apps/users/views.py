import json
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from courses.models import Course
from operation.models import UserCourse, UserFavorate, UserMessage
from organization.models import CourseOrg, Teacher
from utils.mixin_utils import LoginRequiredMixin
from .models import UserProfile,EmailVerifyRecord
from django.db.models import Q
from django.views.generic.base import View
from .forms import LoginFrom, RegisterForm, ForgetForm, ModifyForm, UploadImageForm, UserInfoForm
from django.contrib.auth.hashers import make_password
from utils.email_send import send_register_email
from pure_pagination import Paginator,EmptyPage,PageNotAnInteger



# Create your views here.


class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username)|Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None

class LogoutView(View):
    def get(self, request):
        logout(request)
        from django.core.urlresolvers import reverse
        return HttpResponseRedirect(reverse('index'))



class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')
    def post(self, request):
        login_form = LoginFrom(request.POST)
        #form表单的验证
        # is_valid()就是用来判断form表单数据中的errors是否为空 如果为空及返回true 否则为false
        if login_form.is_valid():
            user_name = request.POST.get('username', '')
            pass_word = request.POST.get('password', '')
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return render(request, 'index.html')
                else:
                    return render(request, 'login.html', {'msg':'用户未激活'})
            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误'})
        else:
            return render(request, 'login.html', {'login_form':login_form})

# def user_login(request):
#     if request.method == 'POST':
#         user_name = request.POST.get('username', '')
#         pass_word = request.POST.get('password', '')
#         user = authenticate(username=user_name, password=pass_word)
#         if user is not None:
#             login(request, user)
#             return render(request, 'index.html')
#         else:
#             return render(request, 'login.html', {'msg':'用户名或密码错误'})
#
#     elif request.method == 'GET':
#         return render(request, 'login.html')

#账号激活
class ActiveUserView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request, 'active_fail.html')
        return render(request, 'login.html')

class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'register.html', {'register_form':register_form})

    def post(self,request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get('email', '')
            if UserProfile.objects.filter(email=user_name):
                return render(request, "register.html", {"register_form": register_form, "msg": "用户已经存在"})
            pass_word = request.POST.get("password", "")
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.is_active = False
            user_profile.password = make_password(pass_word)
            user_profile.save()

            user_message = UserMessage()
            user_message.user = user_profile.id
            user_message.message = '欢迎注册慕学网'
            user_message.save()

            send_register_email(user_name, 'register')
            return render(request, 'login.html')
        else:
            return render(request, 'register.html', {'register_form':register_form})


class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, 'forgetpwd.html', {'forget_form':forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email', '')
            send_register_email(email, 'forget')
            return render(request, 'send_success.html')
        else:
            return render(request, 'forgetpwd.html', {'forget_form':forget_form})

class ResetView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        # print(all_records)
        if all_records:
            for record in all_records:
                email = record.email
                return render(request, 'password_reset.html', {'email':email})
        else:
            return render(request, 'active_fail.html')
        return render(request, 'login.html')


class ModifyView(View):
    def post(self,request):
        modify_form = ModifyForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            email = request.POST.get('email', '')
            if pwd1 != pwd2:
                return render(request, 'password_reset.html', {'email':email, 'msg':'密码不一致'})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd1)
            user.save()
            return render(request, 'login.html')
        else:
            email = request.POST.get('email', '')
            return render(request, 'password_reset.html', {'email':email, 'modify_form':modify_form})


#用户个人信息
class UserInfoView(LoginRequiredMixin,View):
    def get(self, request):
        return render(request, 'usercenter-info.html')

    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        #instance为指定的是修改某个用户的信息，否则会新增数据
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')



# 用户头像修改
class UploadImageView(LoginRequiredMixin, View):
    def post(self,request):
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            #方法一：
            # image = image_form.cleaned_data['image']
            # request.user.image = image
            # request.user.save()

            #方法二 在image_form参数中添加了instance 否则无效
            image_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail"}', content_type='application/json')


#个人中心修改密码
class UpdatePwdView(View):
    def post(self,request):
        modify_form = ModifyForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            if pwd1 != pwd2:
                return HttpResponse('{"status":"fail", "msg":"两次密码不一致"}', content_type='application/json')
            user = request.user
            user.password = make_password(pwd1)
            user.save()
            return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')


# 个人中心发送邮箱验证码
class SendEmailCodeView(LoginRequiredMixin,View):
    def get(self, request):
        email = request.GET.get('email', '')
        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email":"邮箱已存"}', content_type='application/json')
        send_register_email(email, "update_email")
        return HttpResponse('{"status":"success"}', content_type='application/json')


#修改邮箱
class UpdateEmailView(View):
    def post(self, request):
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')
        if EmailVerifyRecord.objects.filter(email=email, code=code, send_type='update_email'):
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')

        else:
            return HttpResponse('{"email":"验证码错误"}', content_type='application/json')

# 个人中心我的课程
class MyCourseView(LoginRequiredMixin,View):
    def get(self, request):
        all_course = UserCourse.objects.filter(user=request.user)
        return render(request, 'usercenter-mycourse.html', {
            'all_course':all_course
        })


# 个人中心我的收藏机构
class MyFavOrgView(View):
    def get(self, request):
        org_list = []
        fav_orgs = UserFavorate.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            org_id = fav_org.fav_id
            org = CourseOrg.objects.get(id=int(org_id))
            org_list.append(org)
        return render(request, 'usercenter-fav-org.html',{
            'org_list':org_list
        })


# 个人中心我的收藏讲师
class MyFavTeacherView(View):
    def get(self, request):
        teacher_list = []
        fav_teachers = UserFavorate.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=int(teacher_id))
            teacher_list.append(teacher)
        return render(request, 'usercenter-fav-teacher.html',{
            'teacher_list':teacher_list
        })


# 个人中心我的收藏课程
class MyFavCourseView(View):
    """
    我收藏的课程
    """
    def get(self, request):
        course_list = []
        fav_courses = UserFavorate.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)
        return render(request, 'usercenter-fav-course.html', {
            "course_list": course_list
        })



class MyMessageView(View):
    def get(self, request):
        all_message = UserMessage.objects.filter(user=request.user.id)

        all_unread_message = UserMessage.objects.filter(user=request.user.id, has_read=False)
        for unread_message in all_unread_message:
            unread_message.has_read = True
            unread_message.save()

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_message, 1, request=request)
        message = p.page(page)

        return render(request, 'usercenter-message.html',{
            'all_message':message
        })