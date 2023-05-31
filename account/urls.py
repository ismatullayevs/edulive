from django.urls import path, include
from .account_views import views
from .students import views as s_views
from django.contrib.auth.views import LoginView, LogoutView
from account.utils.payme import PaymeView

app_name = 'account'

urlpatterns = [
    path('login/', views.login_view, name='log_in'),
    path('logout/', views.log_out, name='log_out'),
    path('signup/', views.register, name='sign_up'),
    path('verify/', views.verify, name='verify'),
    path('resend/', views.otp, name='resend'),

    path('teacher/edit/', views.user_update_view, name='teacher_edit'),

    # change
    path(
        "password_change/", views.PasswordChangeView.as_view(), name="password_change"
    ),
    path(
        "password_change/done/",
        views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path("password_reset/", views.PasswordResetView.as_view(template_name='account/change/reset_password.html',
                                                            email_template_name='new/reset_password_email.html'),
         name="password_reset"),
    path(
        "password_reset/done/",
        views.PasswordResetDoneView.as_view(template_name='account/change/reset_password_done.html'),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(template_name='account/change/reset_password_confirm.html'),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        views.PasswordResetCompleteView.as_view(template_name='account/change/reset_done.html'),
        name="password_reset_complete",
    ),

    path('enroll-course/', s_views.StudentEnrollCourseView.as_view(), name='student_enroll_course'),
    path('courses/', s_views.StudentCourseListView.as_view(), name='student_course_list'),
    # path('course/<slug:group_s>/<slug:course_s>/', s_views.StudentCourseDetailView.as_view(),
    #      name='student_course_detail'),
    path('course/<slug:group_s>/<slug:course_s>/', s_views.student_course_module_list, name='student_course_detail'),
    path('course/<pk>/<module_id>/', s_views.StudentCourseDetailView.as_view(), name='student_course_detail_module'),
    # path('profile/', views.dashboard_student, name='stdudent_dashboard'),

    path('profile/', s_views.StudentdDashboardView.as_view(), name='stdudent_dashboard'),
    path('profile/edit/', s_views.student_update_view, name='user_edit_profile'),
    path('payment_info/', s_views.StudentPaymentInfo.as_view(), name='payment_info'),

    # path('module/<slug:course_slug>/<int:pk>/', s_views.ModuleContentDetail.as_view(), name='module_detail'),
    path('module/<slug:course_slug>/<int:pk>/', s_views.ModuleDetailView.as_view(), name='module_detail'),

    # path('quiz/', include('students.quiz.urls')),
    path('sertificate/<uuid>/', s_views.ViewPDF.as_view(), name='sertificate'),
    path('payment', PaymeView.as_view(), name='payment'),
]
