from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
from operation.models import UserFavorate
from .models import CourseOrg,CityDict,Teacher
from courses.models import Course
from django.views.generic.base import View
from django.db.models import Q
from pure_pagination import Paginator,EmptyPage,PageNotAnInteger
from .forms import UserAskForm
from courses.models import Course
from django.core import serializers

class OrglistView(View):
    def get(self, request):
        #课程机构
        all_orgs = CourseOrg.objects.all()

        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_orgs = all_orgs.filter(
                Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords))

        #热门排行
        hot_org = all_orgs.order_by('-click_nums')[:3]
        #城市
        all_city = CityDict.objects.all()
        #取出筛选城市
        city_id = request.GET.get('city', '')
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))

        #类别筛选
        category = request.GET.get('ct', '')
        if category:
            all_orgs = all_orgs.filter(category=category)

        #筛选学习人数
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':
                all_orgs = all_orgs.order_by("-student")
            elif sort == 'courses':
                all_orgs = all_orgs.order_by("-course_num")



        org_num = all_orgs.count()
        #对课程机构进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_orgs, 2, request=request)
        orgs = p.page(page)
        return render(request, 'org-list.html',{
            'all_orgs':orgs,
            'all_city':all_city,
            'org_num':org_num,
            'city_id':city_id,
            'category':category,
            'hot_org':hot_org,
            'sort':sort
        })

class AddUserAskView(View):
    '''
    用户咨询表单提交
    '''
    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            user_ask = userask_form.save(commit=True)
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"添加出错"}', content_type='application/json')


class OrgHomeView(View, ):
    def get(self,request, org_id):
        current_page = 'home'
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorate.objects.filter(user=request.user, fav_id=int(course_org.id), fav_type=2):
                has_fav = True
        all_courses = course_org.course_set.all()[:3]
        all_teachers = course_org.teacher_set.all()[:1]
        return render(request, 'org-detail-homepage.html',{
            'all_courses':all_courses,
            'all_teachers':all_teachers,
            'course_org':course_org,
            'current_pag':current_page,
            'has_fav':has_fav
        })
class OrgCourseView(View):
    def get(self, request, org_id):
        current_page = 'course'
        course_org = CourseOrg.objects.get(id=int(org_id))
        all_course = course_org.course_set.all()
        return render(request, 'org-detail-course.html', {
            'all_course':all_course,
            'course_org':course_org,
            'current_page':current_page
        })

class OrgDescView(View):
    def get(self,request, org_id):
        current_page = 'desc'
        course_org = CourseOrg.objects.get(id=int(org_id))
        return render(request, 'org-detail-desc.html',{
            'course_org':course_org,
            'current_page':current_page
        })

class OrgTeacherView(View):
    def get(self,request, org_id):
        current_page = 'teacher'
        course_org = CourseOrg.objects.get(id=int(org_id))
        all_teacher = course_org.teacher_set.all()
        return render(request, 'org-detail-teachers.html', {
            'current_page':current_page,
            'course_org':course_org,
            'all_teacher':all_teacher
        })



class AddFavView(View):
    """
    用户收藏，用户取消收藏
    """
    def post(self, request):
        fav_id = request.POST.get('fav_id', 0)
        fav_type = request.POST.get('fav_type', 0)

        if not request.user.is_authenticated():
            #判断用户登录状态
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')

        exist_records = UserFavorate.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
        print(serializers.serialize('json', exist_records))
        if exist_records:
            #如果记录已经存在， 则表示用户取消收藏
            exist_records.delete()

            return HttpResponse('{"status":"success", "msg":"收藏"}', content_type='application/json')
        else:
            user_fav = UserFavorate()
            if int(fav_id) > 0 and int(fav_type) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.fav_type = int(fav_type)
                user_fav.save()



                return HttpResponse('{"status":"success", "msg":"已收藏"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"fail", "msg":"收藏出错"}', content_type='application/json')

class TeacherListView(View):
    def get(self,request):
        teacher_list = Teacher.objects.all()

        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            teacher_list = teacher_list.filter(Q(name__icontains=search_keywords)|Q(work_position__icontains=search_keywords))

        #显示人气排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'hot':
                teacher_list = teacher_list.order_by('-click_nums')

        sorted_teacher = Teacher.objects.all().order_by('-click_nums')[:3]

        #讲师分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(teacher_list, 1, request=request)
        teachers = p.page(page)

        return render(request, 'teachers-list.html', {
            'teacher':teachers,
            'sorted_teacher':sorted_teacher,
            'sort':sort
        })

class TeacherDetail(View):
    def get(self, request, teacher_id):
        teacher = Teacher.objects.get(id=int(teacher_id))
        all_course = Course.objects.filter(teacher=teacher)
        sorted_teacher = Teacher.objects.all().order_by('-click_nums')[:3]

        has_teacher_favs = False
        if UserFavorate.objects.filter(user=request.user, fav_id=teacher.id, fav_type=3):
            has_teacher_favs = True

        has_org_favs = False
        if UserFavorate.objects.filter(user=request.user, fav_id=teacher.org.id, fav_type=2):
            has_org_favs = True

        return render(request, 'teacher-detail.html', {
            'teacher':teacher,
            'all_course':all_course,
            'sorted_teacher':sorted_teacher,
            'has_teacher_favs':has_teacher_favs,
            'has_org_favs':has_org_favs
        })


