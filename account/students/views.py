import base64

from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import get_template
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, ListView, DetailView, UpdateView
from django.views.generic.base import TemplateResponseMixin, View
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from account.forms import CourseEnrollForm, CommentForm, UpdateFormUser, StudentUpdateForm
from account.models import Students, CustomUser
from account.utils.courses import generate_pay_url
from courses.models import GroupCourse, GroupModuleContent, Course, Transaction, GroupContents, Content, Module, \
    Comments
from django.utils.translation import gettext_lazy as _

from quiz.models import Sertificate

from xhtml2pdf import pisa


# kursga yozilish

class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    group = None
    r_user = None

    def dispatch(self, request, *args, **kwargs):
        print('hello')
        try:
            self.r_user = Students.objects.get(user=request.user)
        except:
            self.r_user = None
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        form = CourseEnrollForm(None, self.r_user, request.POST or None, request.FILES or None)

        if form.is_valid():
            return self.form_valid(form)

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.group = form.cleaned_data['group']

        if not self.r_user:
            pasport = form.cleaned_data['pasport']
            selfi_pasport = form.cleaned_data['selfi_pasport']
            date_of_birth = form.cleaned_data['date_of_birth']
            self.r_user = Students.objects.create(
                user=self.request.user,
                pasport=pasport,
                selfi_pasport=selfi_pasport,
                date_of_birth=date_of_birth
            )

            # self.course.students.add(std)
            # self.group.students.add(std)
            # elif self.r_user and self.r_user not in self.course.students.all() and self.r_user not in self.group.students.all():
            # self.course.students.add(std)
            # self.group.students.add(std)

        url = generate_pay_url(self.course, self.group, self.r_user)
        return redirect(url)
        # return super().form_valid(form)

    def form_invalid(self, form):
        return redirect(reverse('course:course_detail', args=[self.course.slug]))

    def get_success_url(self):
        return reverse_lazy('account:student_course_detail', args=[self.group.slug, self.course.slug])


# kurl list
class StudentCourseListView(LoginRequiredMixin, ListView):
    model = GroupCourse
    template_name = 'students/courses.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__user__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# class StudentCourseListView(LoginRequiredMixin, ListView):
#     model = GroupModuleContent
#     template_name = 'students/module_list.html'
#
#     def dispatch(self, request, group_s=None, *args, **kwargs):
#         self.object_list
#
#         return super().dispatch(request, *args, **kwargs)

def student_course_module_list(request, group_s, course_s):

    modules = GroupModuleContent.objects.filter(module__course__groupcourse__slug=group_s).select_related('module',
                                                                                                          'module__course').prefetch_related(
        'content_type', 'groupcontents', 'groupcontents__content_type')
    print(modules)
    return render(request, 'students/module_list.html', {'modules': modules, 'course_s': course_s})


class StudentCourseDetailView(LoginRequiredMixin, DetailView):
    model = GroupCourse
    template_name = 'students/module_list.html'
    slug_url_kwarg = 'group_s'

    def get_queryset(self):
        # q = GroupCourse.objects.get(id=20).select_related('course').prefetch_related('students','course__modules','course__modules__contents')
        qs = super().get_queryset()
        return qs.filter(students__user__in=[self.request.user]).select_related('course').prefetch_related('students',
                                                                                                           'course__modules',
                                                                                                           "course__modules__contents")


class StudentdDashboardView(TemplateResponseMixin, View):
    template_name = 'students/index.html'

    def get(self, request):
        try:
            user = Students.objects.get(user=request.user)
            courses = user.groupcourse.all()
            sum = []
            for x in courses:
                if x.progress() == '100':
                    sum.append(x)
            compl = len(sum)
        except:
            user = []
            courses = []
            compl = ''
        # user = get_object_or_404(Students,user=request.user)
        return self.render_to_response({'user': user, 'courses': courses, 'complated': compl})


def student_update_view(request):
    form = UpdateFormUser(instance=request.user)
    form_change = PasswordChangeForm(user=request.user)

    if request.method.lower() == 'post':
        print('postga keldi')
        form = UpdateFormUser(request.POST or None, request.FILES or None, instance=request.user)
        print(form.is_valid())
        if form.is_valid():
            phone = form.instance.phone_number

            if len(phone) == 12 and str(phone).isdigit():
                obj = form.save(commit=False)
                obj.save()
            else:
                messages.warning(request, _("Telfon raqam noto'g'ri kiritildi"))
            messages.success(request, "Ma'lumotlar muvaffaqiyatli o'zgartirildi")

    context = {
        'form': form,
        'form_change': form_change
    }
    return render(request, 'students/edit_profile_std.html', context)


class UserUpdateView(UpdateView):
    model = CustomUser
    form_class = UpdateFormUser
    template_name = 'students/edit_profile_std.html'
    std = None
    form_std = StudentUpdateForm()
    s_pk = None

    def dispatch(self, request, pk):
        try:
            self.std = Students.objects.get(user=request.user)
            self.form_std = StudentUpdateForm(instance=self.std)
            self.s_pk = self.std.pk
        except:
            pass

        self.user = request.user
        return super().dispatch(request, pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.std:
            context['form_std'] = self.form_std
            context['std'] = self.s_pk
            context['std_found'] = True
        else:
            context['std_found'] = False

        context['form_change'] = PasswordChangeForm(user=self.user)
        return context

    def form_valid(self, form):
        phone = form.instance.phone_number
        email = form.instance.email

        if len(phone) == 12 and str(phone).isdigit():
            self.object = form.save()
            messages.success(self.request, "Ma'lumotlar muvaffaqiyatli o'zgartirildi")
            return self.render_to_response(self.get_context_data(form=form, user=True, object=self.object))
        else:
            messages.error(self.request, 'telefon raqam xato kiritildi')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return self.render_to_response(self.get_context_data(form=form, user=True))


class StudentPaymentInfo(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'students/payment_info.html'

    def get_queryset(self):
        qs = super(StudentPaymentInfo, self).get_queryset()
        return qs.filter(student__user=self.request.user)


class ModuleDetailView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = 'students/module_content.html'

    def dispatch(self, request, course_slug, pk, *args, **kwargs):
        self.object = get_object_or_404(GroupModuleContent, pk=pk)
        self.module_contents = self.object.module.contents.select_related('module').all()
        pc = GroupContents.objects.all()
        self.group_contents = self.object.groupcontents.select_related('module', 'content_type').all()
        self.comments = Comments.objects.select_related('user', 'user__students').prefetch_related('user').filter(
            group_module=self.object)
        return super().dispatch(request, course_slug, pk, *args, **kwargs)

    def get(self, request, course_slug, pk):
        print('object')
        return self.render_to_response({
            'object': self.object,
            'contents': self.module_contents,
            'group_contents': self.group_contents,
            'comments': self.comments,
            'form': CommentForm()
        })

    def post(self, request, course_slug, pk, *args, **kwargs):
        form = CommentForm(request.POST or None)
        if form.is_valid():
            content = request.POST.get('content')
            # reply_id = request.POST.get('comment_id')
            comment_qs = None
            # if reply_id:
            #     comment_qs = self.get_object().comments.get(id=reply_id)
            comment = self.object.comments.create(
                user=request.user,
                content=content,
                reply_id=comment_qs
            )
            comment.save()
            # context = {'comment': comment}
            return redirect(reverse('account:module_detail', kwargs={'course_slug': course_slug, 'pk': pk}))
        return self.render_to_response({
            'object': self.object,
            'contents': self.module_contents,
            'group_contents': self.group_contents,
            'comments': self.comments,
            'form': form
        })


class ModuleContentDetail(LoginRequiredMixin, DetailView):
    model = GroupModuleContent
    template_name = 'students/module_content.html'
    course = None
    modules = None

    def get_queryset(self):
        # q = GroupModuleContent.objects.prefetch_related('module__contents__content_type').all()
        qs = super(ModuleContentDetail, self).get_queryset()
        return qs.filter(groupcourse__students__user__in=[self.request.user]).prefetch_related(
            'comments', 'module__contents').select_related('module')

    def dispatch(self, request, course_slug, *args, **kwargs):
        try:
            self.course = Course.objects.get(slug=course_slug)
            self.modules = self.course.modules.all()
        except:
            self.course = None
        # if self.course:
        return super().dispatch(request, course_slug, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['modules'] = self.modules
        context['course'] = self.course
        context['form'] = CommentForm()
        return context

    def post(self, request, course_slug, *args, **kwargs):
        form = CommentForm(request.POST or None)
        if form.is_valid():
            content = request.POST.get('content')
            reply_id = request.POST.get('comment_id')
            comment_qs = None
            if reply_id:
                comment_qs = self.get_object().comments.get(id=reply_id)
            comment = self.get_object().comments.create(
                user=request.user,
                content=content,
                reply_id=comment_qs
            )
            comment.save()
            context = {'comment': comment}
            return render(request, 'students/comment/comment_detail.html', context)
            # return render(request,)
        return HttpResponse(
            ''' fail '''
        )


class ViewPDF(View):
    sertificate = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.sertificate = Sertificate.objects.get(uuid=kwargs['uuid'])
            print(self.sertificate)
        except Sertificate.DoesNotExist:
            self.sertificate = None
        return super(ViewPDF, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        template_path = 'students/sertificate.html'
        context = {'sert': self.sertificate}
        # Create a Django response object, and specify content_type as pdf
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f' filename="{request.user.last_name}.pdf"'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
            html, dest=response)
        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
