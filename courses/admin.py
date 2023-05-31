from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
# Register your models here.
from courses.models import (
    Course, Module, Subject, GroupCourse, Content, ItemBase, Video, Text, Transaction, GroupModuleContent, GroupContents
)
from embed_video.admin import AdminVideoMixin


class MyVideoAdmin(AdminVideoMixin, Video):
    pass


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'active']
    list_editable = ['active']


@admin.register(GroupCourse)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'course']


@admin.register(Content)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'module']


@admin.register(GroupContents)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'module']


admin.site.register(Transaction)
admin.site.register(GroupModuleContent)
admin.site.register(Video)
