from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView
from django.views.generic.base import TemplateResponseMixin, View

from account.forms import CourseEnrollForm
from account.models import Students
from courses.models import Subject, Course


class HomePage(TemplateResponseMixin, View):

    def get(self, request):
        return render(request, 'course/pages/index.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


home_page = HomePage.as_view()


class CourseListView(TemplateResponseMixin, View):
    template_name = 'course/pages/courses.html'

    def get(self, request, subject=None):
        subjects = Subject.objects.annotate(total_courses=Count(
            'courses', filter=Q(courses__active=True)))
        courses = Course.objects.filter(active=True).annotate(
            total_modules=Count('modules')
        )

        if request.GET.get('search_courses'):
            query = request.GET.get('search_courses')
            courses = courses.filter(
                Q(title__icontains=query) | Q(subject__title__icontains=query), active=True)

        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            courses = courses.filter(subject=subject, active=True)

        return self.render_to_response({
            'subjects': subjects,
            'subject': subject,
            'courses': courses
        })


course_list_view = CourseListView.as_view()


class CourseDetailView(DetailView):
    model = Course
    template_name = 'course/pages/detail-course.html'
    r_user = None
    group = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.r_user = Students.objects.get(user=self.request.user)
            try:
                self.group = self.r_user.groupcourse.get(course__slug=self.kwargs['slug'])
            except:
                self.group = None
        except:
            self.r_user = None

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['r_user'] = self.r_user
        context['group'] = self.group
        context['enroll'] = CourseEnrollForm(self.object, self.r_user,
                                             initial={
                                                 'course': self.object,
                                             }
                                             )

        # form = CourseEnrollForm(self.request.POST, self.request.FILES)
        return context
