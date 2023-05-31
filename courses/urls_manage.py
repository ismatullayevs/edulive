from django.urls import path
from courses.manage_view import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'manage'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('mine/', views.manage_course_list, name="manage_course_list"),

    # htmx
    path('create/', views.course_form, name='course_form'),
    path('htmx/<pk>/edit/', views.course_update_view, name='course_edit'),
    path('htmx/<pk>/delete/', views.delete_course, name='course_delete'),
    path('htmx/<pk>/detail/', views.course_detail, name='detail_course'),

    path('<pk>/module/', views.course_module_update_view,
         name='course_module_update'),

    path('<pk>/', views.manage_course_detail,
         name='manage_course_detail'),

    # manage module htmx
    path('htmx/delete-modul/<pk>/', views.delete_modul, name='delete-modul'),
    path('htmx/update-modul/<pk>/', views.update_modul, name='update-modul'),
    path('htmx/create-model-form/', views.module_form, name='create_modul_form'),
    path('htmx/detail-modul/<pk>/', views.detail_modul, name='detail-modul'),

    # module
    path('module/<int:module_id>/content/<model_name>/create/', views.ContentCreateUpdateView.as_view(),
         name='module_content_create'),

    path('module/<int:module_id>/content/<model_name>/<id>/', views.ContentCreateUpdateView.as_view(),
         name='module_content_update'),
    path('content/<int:id>/delete/', views.ContentDeleteView.as_view(), name='module_content_delete'),
    path('module/<int:module_id>/', views.ModuleContentListView.as_view(), name='module_content_list'),
    path('module/<module_id>/<content_id>/detail/<item_id>/', views.content_detail, name='module_content_detail'),

    # create groups
    path('htmx/group/group-form/<pk>', views.group_form, name='group_form'),
    path('htmx/group/create-group/<pk>/', views.GroupCourseCreateView.as_view(), name='create-group'),
    path('htmx/group/detail/<pk>/<slug:slug>/', views.detail_groupcourse, name='detail_group'),
    path('htmx/group/update/<pk>/<slug:slug>/', views.update_group, name='update_group'),
    path('htmx/group/delete/<pk>/<slug>/', views.GroupCourseCreateView.as_view(), name='delete_group'),

    # manage group
    path('manage/group/list/', views.GroupCourseListView.as_view(), name='manage_group_list'),
    path('manage/group/detail/<slug:slug>/', views.GroupCourseDetailViev.as_view(), name='manage_group_detail'),
    path('manage/group/<slug>/contents/<int:id>/', views.GroupContentView.as_view(), name='manage_group_contents'),

    path('manage/group/active/<slug:slug>/', views.group_active, name='active_group'),

    # htmx schedule
    path('htmx/manage/group/form/<slug>/', views.group_schedule_form, name='group_schedule'),
    path('htmx/<group_m_id>/content/<model_name>/create/', views.GroupContentCreateUpdateView.as_view(),
         name='group_content_create'),
    path('htmx/<int:group_m_id>/content/<str:model_name>/<int:id>/', views.GroupContentCreateUpdateView.as_view(),
         name='group_content_update'),
    # path('htmx/<slug:slug>/<int:id>/<str:model_name>/',view.GroupContentCreateUpdateView.as_view(), name='group_create_update'),
    path('htmx/<int:group_m_id>/content/<int:item_id>/detail/', views.detail_group_content,
         name='group_content_detail'),
    path('htmx/<int:group_m_id>/content/<int:item_id>/delete/', views.GroupContentDeleteView.as_view(),
         name='group_content_delete'),
]

#urlpatterns += static(settings.MEDIA_URL,
#                      document_root=settings.MEDIA_ROOT)
#urlpatterns += static(settings.STATIC_URL,
#                      document_root=settings.STATIC_ROOT)
