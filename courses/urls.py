from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from courses.index_view import views as index

app_name = 'course'

urlpatterns = [
    path('', index.home_page, name='homepage'),
    path('course/', index.course_list_view, name='course_list'),

    path('subject/<slug:subject>/', index.CourseListView.as_view(),
         name='course_list_subject'),
    path('<slug:slug>/', index.CourseDetailView.as_view(), name='course_detail'),

    # dashboard urls
    path('course/manage/', include('courses.urls_manage')),
]

#if settings.DEBUG:
#    urlpatterns += static(settings.MEDIA_URL,
#                          document_root=settings.MEDIA_ROOT)

#urlpatterns += static(settings.STATIC_URL,
#                      document_root=settings.STATIC_ROOT)
