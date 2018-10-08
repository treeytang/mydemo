
import xadmin

from .models import EmailVerifyRecord,Banner
from  xadmin import views


#设置主题功能
class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True

# 设置后台显示的头和脚 以及设置分类的折叠
class GlobalSetting(object):
    site_title = '慕学后台管理系统'
    site_footer = '慕学在线网'
    menu_style = 'accordion'


# 邮箱验证
class EmailVerifyRecordAdmin(object):
    #在后台管理系统中需要显示的字段
    list_display = ['code', 'email', 'send_type', 'send_time']
    #在后台管理系统中可以提供搜索的字段
    search_fields = ['code', 'email', 'send_type']
    #过滤器
    list_filter = ['code', 'email', 'send_type', 'send_time']

class BannerAdmin(object):

    # 在后台管理系统中需要显示的字段
    list_display = ['title', 'image', 'url', 'index', 'add_time']
    # 在后台管理系统中可以提供搜索的字段
    search_fields = ['title', 'image', 'url', 'index']
    list_filter = ['title', 'image', 'url', 'index', 'add_time']


xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
xadmin.site.register(Banner, BannerAdmin)
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView,GlobalSetting)