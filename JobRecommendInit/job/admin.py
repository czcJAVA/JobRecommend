from django.contrib import admin

from job.models import JobData, UserList

# 后台里面的认证和授权 可以隐藏掉
from django.contrib import admin
from django.contrib.auth.models import User, Group

# 取消注册 User 和 Group 模型
admin.site.unregister(User)
admin.site.unregister(Group)

# 设置管理后台的头部标题
admin.site.site_header = '招聘后台管理'
# 设置管理后台在浏览器标签页中显示的标题
admin.site.site_title = '招聘后台管理'
# 设置管理后台主页的标题
admin.site.index_title = '招聘后台管理'





class UserListAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'user_name', 'pass_word')  # 列表中显示的字段
    search_fields = ('user_id', 'user_name')  # 可搜索的字段
    # 设置默认的排序方式，这里按照 id 字段进行排序
    ordering = ['user_id']

admin.site.register(UserList, UserListAdmin)


# Register your models here.
class JobDataAdmin(admin.ModelAdmin):
    list_display = (
    'job_id', 'name', 'salary', 'place', 'education', 'experience', 'company', 'label', 'scale', 'href', 'key_word')
    search_fields = ('name', 'company', 'place')
    list_filter = ('education', 'experience', 'scale')
    # 设置默认的排序方式，这里按照 id 字段进行排序
    ordering = ['job_id']


admin.site.register(JobData, JobDataAdmin)


