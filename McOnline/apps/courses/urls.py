from django.conf.urls import url
from .views import CourseListView,CourseDetailView,CourseInfoView, CommentView,AddComentsView,VideoView

urlpatterns = [
    url(r'^list/$', CourseListView.as_view(), name='course_list'),
    url(r'^detail/(?P<course_id>\d+)/$', CourseDetailView.as_view(), name='course_detail'),
    url(r'^info/(?P<course_id>\d+)/$', CourseInfoView.as_view(), name='course_info'),
    url(r'^comment/(?P<course_id>\d+)/$', CommentView.as_view(), name='course_comment'),
    url(r'^add_comment/', AddComentsView.as_view(), name='add_comment'),
    url(r'^video/(?P<video_id>\d+)/$', VideoView.as_view(), name='video_play')
]