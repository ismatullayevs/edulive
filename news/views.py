from django.db.models import Q

from django.shortcuts import render

from django.core.paginator import Paginator
from news.models import Article


def blog_news(request):
    articles = Article.objects.all()
    resent = articles[:5]
    paginator = Paginator(articles, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'object_list': page_obj, 'resent': resent}
    return render(request, 'course/pages/blog_news.html', context)


def blog_single_news(request, pk):
    resent = Article.objects.all()[:5]
    article = Article.objects.get(pk=pk)
    context = {'object': article, 'resent': resent}
    return render(request, 'course/pages/blog_news_single.html', context)


def blog_search(request):
    qs = request.GET.get('search')
    resent = Article.objects.all()[:5]

    try:
        articles = Article.objects.filter(Q(title__icontains=qs) | Q(subtitle__icontains=qs))
    except:
        articles = []
    return render(request, 'course/pages/blog_news.html', context={'object_list': articles, 'resent': resent})


def offerta(request):
    return render(request, 'course/pages/offerta.html')
