from django.urls import path
from news.views import blog_news, blog_single_news, blog_search, offerta

app_name = 'news'

urlpatterns = [
    path('', blog_news, name='news'),
    path('<int:pk>/', blog_single_news, name='single_news'),
    path('search/', blog_search, name='search_news'),
    path('offerta/', offerta, name='offerta'),
]
