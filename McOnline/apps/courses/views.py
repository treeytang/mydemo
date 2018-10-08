from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
from pure_pagination import Paginator,EmptyPage,PageNotAnInteger

from django.views import View
# Create your views here.
from courses.models import Course, CourseResource,Video

from operation.models import UserFavorate, CourseComments,UserCourse
#以Mixin结尾的代表的是基础的View
from utils.mixin_utils import LoginRequiredMixin


class CourseListView(View):
    def get(self, request):
        all_course = Course.objects.all().order_by('-add_time')
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_course = all_course.filter(
                Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords))

        hot_courses = Course.objects.all().order_by('-click_num')[:3]
        #课程排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':
                all_course = all_course.order_by("-students")
            elif sort == 'hot':
                all_course = all_course.order_by("-click_num")


        # 对课程进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_course, 3, request=request)
        courses = p.page(page)
        return render(request, 'course-list.html', {
            'all_course':courses,
            'sort':sort,
            'hot_courses':hot_courses
        })

class CourseDetailView(View):
    def get(self, request, course_id):
        '''
        课程详情页
        '''
        course = Course.objects.get(id=int(course_id))
        # 增加课程点击数
        course.click_num += 1
        course.save()

        has_fav_course = False
        has_fav_org = False
        if request.user.is_authenticated():
            if UserFavorate.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True

            if UserFavorate.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True




        tag = course.tag
        if tag:
            relate_coures = Course.objects.filter(tag=tag)[:1]
        else:
            relate_coures = []


        return render(request, 'course-detail.html', {
            'course':course,
            'relate_course':relate_coures,
            'has_fav_course':has_fav_course,
            'has_fav_org':has_fav_org
        })


class CourseInfoView(LoginRequiredMixin,View):
    '''
    章节信息
    '''
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        course.students += 1
        course.save()
        #查询用户是否已经关联里改课程
        user_course = UserCourse.objects.filter(user=request.user, course=course)
        if not user_course:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()
        #查找出用户课程
        user_courses = UserCourse.objects.filter(course=course)
        #用列表推倒式的方法找出学过该课程的其他用户的id
        user_ids = [user_course.user.id for user_course in user_courses]
        #找出id等于user_ids列表里用户id
        all_user_courses_id = UserCourse.objects.filter(user_id__in=user_ids)
        #取出所有课程的id
        course_ids = [user_course.course.id for user_course in all_user_courses_id]
        #获取学过该课程的用户他们学过什么课程
        relate_course = Course.objects.filter(id__in=course_ids).order_by("-click_num")[:5]
        all_resoures = CourseResource.objects.filter(course=course)
        return render(request, 'course-video.html', {
            'course':course,
            'course_resourcer':all_resoures,
            'relate_course':relate_course
        })

class CommentView(LoginRequiredMixin,View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        all_resoures = CourseResource.objects.filter(course=course)
        all_comment = CourseComments.objects.all()
        user_course = UserCourse.objects.filter(user=request.user, course=course)
        if not user_course:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()
        # 查找出用户课程
        user_courses = UserCourse.objects.filter(course=course)
        # 用列表推倒式的方法找出学过该课程的其他用户的id
        user_ids = [user_course.user.id for user_course in user_courses]
        # 找出id等于user_ids列表里用户id
        all_user_courses_id = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程的id
        course_ids = [user_course.course.id for user_course in all_user_courses_id]
        # 获取学过该课程的用户他们学过什么课程
        relate_course = Course.objects.filter(id__in=course_ids).order_by("-click_num")[:5]
        return render(request, 'course-comment.html', {
            'course':course,
            'course_resourcer': all_resoures,
            'all_comment':all_comment,
            'relate_course': relate_course
        })

class AddComentsView(View):
    def post(self, request):
        if not request.user.is_authenticated():
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')

        course_id = request.POST.get('course_id', 0)
        comment = request.POST.get('comments', '')
        if int(course_id) > 0 and comment:
            course_comment = CourseComments()
            course = Course.objects.get(id=int(course_id))
            course_comment.user = request.user
            course_comment.course = course
            course_comment.comments = comment
            course_comment.save()
            return HttpResponse('{"status":"success", "msg":"添加成功"}', content_type='application/json')
        else:                                                                                   
            return HttpResponse('{"status":"fail", "msg":"添加失败"}', content_type='application/json')


class VideoView(View):
    '''
    视频播放页面
    '''
    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))
        course = video.lesson.course
        all_resoures = CourseResource.objects.filter(course=course)
        all_comment = CourseComments.objects.all()
        user_course = UserCourse.objects.filter(user=request.user, course=course)
        if not user_course:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()
        # 查找出用户课程
        user_courses = UserCourse.objects.filter(course=course)
        # 用列表推倒式的方法找出学过该课程的其他用户的id
        user_ids = [user_course.user.id for user_course in user_courses]
        # 找出id等于user_ids列表里用户id
        all_user_courses_id = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程的id
        course_ids = [user_course.course.id for user_course in all_user_courses_id]
        # 获取学过该课程的用户他们学过什么课程
        relate_course = Course.objects.filter(id__in=course_ids).order_by("-click_num")[:5]
        return render(request, 'course-play.html', {
            'course':course,
            'course_resourcer': all_resoures,
            'all_comment':all_comment,
            'relate_course': relate_course,
            'video':video
        })