from django.urls import path
from quiz import views

app_name = 'quiz'

urlpatterns = [
    path('manage/quiz/list/', views.QuizListView.as_view(), name='quiz_list'),
    path('manage/quiz/detail/<pk>', views.detail_course_quiz, name='detail_quiz'),
    path('manage/quiz/create/', views.QuizCreateUpdateview.as_view(), name='create_quiz'),
    path('manage/quiz/update/<id>/', views.QuizCreateUpdateview.as_view(), name='update_quiz'),
    path('manage/quiz/delete/<id>/', views.QuizCreateUpdateview.as_view(), name='delete_quiz'),

    path('manage/quiz/<quiz_id>/questions/', views.AddQuestionsView.as_view(), name='add_questions'),
    # path('manage/quiz/<quiz_id>/questions/form/', views.question_form, name='question_form'),

    # path('manage/<quiz_id>/quiz/<pk>/answer/form/', views.answer_form, name='answer_form'),
    # path('manage/answer/form/<quiz_id>', views.answer_form, name='answer_form'),
    # path('manage/<quiz_id>/question/<pk>/answer/', views.answer, name='create_answer'),

    # path('manage/<quiz_id>/question/<pk>/answer/update/', views.AnswerUpdateView.as_view(), name='update_answer'),

    path('manage/quiz/active/<int:pk>', views.quiz_active, name='quiz_active'),

    path('create/question/<quiz_id>', views.question_form, name='create_question'),

    path('update/question/<question_id>', views.update_question, name='update_question'),
    path('delete/question/<question_id>', views.delete_question, name='delete_question'),

    # students
    path('', views.StudentQuizListView.as_view(), name='student_quiz_list'),
    path('<pk>/', views.quiz_view, name='quiz_detail'),
    path('<pk>/save/', views.save_quiz_view, name='save_view'),
    path('<pk>/data/', views.quiz_data_view, name='quiz_data_view'),
]
