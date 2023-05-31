import datetime
import uuid
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Value as V, ImageField
from django.db.models.functions import Substr
from django.db.models.functions import Concat
from django.forms import modelform_factory
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import UpdateView, ListView

from django.views.generic.base import TemplateResponseMixin, View

from account.models import Students, CustomUser
from courses.forms import CourseForm, ModulForm, ModuleFormSet, GroupSchedule, GroupForm
from courses.models import GroupCourse, Course, Module, Content, GroupModuleContent, GroupContents

from django.contrib import messages
from django.apps import apps
from django.utils.text import slugify


class OwnerMixin(object):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'kurs muvaffaqiyatli yuklandi')
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin,
                       LoginRequiredMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview', 'img', 'price']
    success_url = reverse_lazy('course:manage:manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'dashboard/manage/course/form_course.html'
    fields = ['subject', 'title', 'overview', 'img']


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'

    def form_valid(self, form):
        self.object = form.save()
        return redirect('course:manage:detail_course', pk=self.object.id)


course_update_view = CourseUpdateView.as_view()


# Boshqaruv paneli

class Dashboard(TemplateResponseMixin, View):
    template_name = 'dashboard/home/index.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            groups = request.user.groups.values_list('name', flat=True)[0]
        except:
            groups = None
        if groups == 'instructor':
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('course:homepage')

    def get(self, request):
        user = request.user

        courses = Course.objects.filter(owner=user).select_related('owner').prefetch_related('students',
                                                                                             'students__user', )
        # students = list(map(lambda std: std['students'], courses.values('students')))

        count_groups = GroupCourse.objects.filter(course__in=courses).values('slug').count()
        #   f

        students = Students.objects.filter(courses_joined__in=courses).select_related(
            'user').prefetch_related(
            'courses_joined', 'courses_joined__title') \
            .order_by('user').distinct('user') \
            .annotate(
            full_name=Concat(
                'user__last_name', V(' '), 'user__first_name'
            ),
            email=Concat('user__email', V('')),
            phone_number=Substr('user__phone_number', 1, 15),
            image=Concat(V('/media/'), 'user__profile_image', output_field=ImageField()),
            # course=Count('courses_joined')
        ) \
            .values(
            'full_name',
            'image',
            'phone_number',
            'email',
        )

        return self.render_to_response({
            'courses': courses,
            'students': students,
            'groups': None,
            'count_courses': len(courses.values('title')),
            'count_groups': count_groups

        })


dashboard = Dashboard.as_view()


# Kurslar bo'limi
class ManageCourseListView(OwnerCourseMixin, ListView):
    http_method_names = ['get', 'post', 'delete', 'put']
    template_name = 'dashboard/manage/course/list.html'
    student = []
    courses = None

    def dispatch(self, request, *args, **kwargs):
        try:
            groups = request.user.groups.values_list('name', flat=True)[0]
        except:
            groups = None

        if groups == 'instructor':
            if request.method.lower() in self.http_method_names:
                if request.method.lower() == 'post':
                    return self.post(request)
                elif request.method.lower() == 'get':
                    self.courses = Course.objects.filter(owner=request.user)
                    return self.get(request)
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('course:homepage')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        students = Students.objects.filter(courses_joined__in=self.object_list).select_related(
            'user').prefetch_related(
            'courses_joined', 'courses_joined__title') \
            .order_by('user').distinct('user') \
            .annotate(
            full_name=Concat(
                'user__last_name', V(' '), 'user__first_name'
            ),
            email=Concat('user__email', V('')),
            phone_number=Substr('user__phone_number', 1, 15),
            image=Concat(V('/media/'), 'user__profile_image', output_field=ImageField()),
        ) \
            .values(
            'full_name',
            'image',
            'phone_number',
        )

        return self.render_to_response({
            'course_list': self.object_list,
            'students': students
        })

    def post(self, request):
        form = CourseForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            course = form.save(commit=False)
            course.slug = slugify(form.instance.title)
            course.owner = request.user
            try:
                course.save()
            except:
                messages.warning(request, _('Kurs nomi band iltimos takrorlanmas nom kiriting'))
                print(form.errors)
                return render(request, 'dashboard/manage/course/form_course.html', context={'form': form})
            return redirect('course:manage:detail_course', pk=course.id)

        return render(request, 'dashboard/manage/course/form_course.html', context={'form': form})


manage_course_list = ManageCourseListView.as_view()


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk, owner=request.user)
    context = {
        'course': course
    }

    return render(request, 'dashboard/manage/course/course_detail.html', context=context)


def course_form(request):
    try:
        groups = request.user.groups.values_list('name', flat=True)[0]
    except:
        groups = None
    if groups == 'instructor':
        form = CourseForm()
        context = {
            'form': form,
        }
        return render(request, 'dashboard/manage/course/form_course.html', context)
    else:
        return redirect('course:homepage')


def delete_course(request, pk):
    try:
        groups = request.user.groups.values_list('name', flat=True)[0]
    except:
        groups = None
    if groups == 'instructor':
        course = get_object_or_404(Course, id=pk, owner=request.user)
        if request.method == 'POST':
            course.delete()
            return HttpResponse("")
        context = {
            'course': course,
        }
        return render(request, 'dashboard/manage/course/delete.html', context=context)
    else:
        return redirect('course:homepage')


class ManageCourseDetailView(OwnerCourseMixin, TemplateResponseMixin, View):
    permission_required = ['courses.add_course', 'courses.add_module']
    template_name = 'dashboard/manage/course/course_detail_modul.html'
    http_method_names = ['get', 'post', 'delete']
    course = None
    group = None

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.http_method_names:
            try:
                self.course = get_object_or_404(
                    Course, pk=kwargs['pk'], owner=request.user)
                self.group = self.course.groupcourse.all()
            except:
                pass

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        return self.render_to_response(
            {
                'course': self.course,
                'groups': self.group,
            }
        )

    def post(self, request, *args, **kwargs):
        form = ModulForm(request.POST)
        if form.is_valid():
            modul = form.save(commit=False)
            modul.course = self.course
            modul.save()
            return redirect('course:manage:detail-modul', pk=modul.id)
        else:
            return render(request, 'dashboard/manage/module/modul_form.html', context={'form': form, })


manage_course_detail = ManageCourseDetailView.as_view()


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'dashboard/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)

    def dispatch(self, request, pk):
        try:
            groups = request.user.groups.values_list('name', flat=True)[0]
        except:
            groups = None
        if groups == 'instructor':
            self.course = get_object_or_404(Course, id=pk, owner=request.user)
            return super().dispatch(request, pk)
        else:
            return redirect('course:homepage')

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response(
            {'course': self.course,
             'formset': formset
             }
        )

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('course:manage:manage_course_list')
        return self.render_to_response({
            'course': self.course,
            'formset': formset
        })


course_module_update_view = CourseModuleUpdateView.as_view()


# module htmx
def delete_modul(request, pk):
    try:
        groups = request.user.groups.values_list('name', flat=True)[0]
    except:
        groups = None
    if groups == 'instructor':
        modul = get_object_or_404(Module, id=pk, course__owner=request.user)

        if request.method == 'DELETE':
            modul.delete()
            return HttpResponse("")
    else:
        return redirect('course:homepage')


def detail_modul(request, pk):
    try:
        groups = request.user.groups.values_list('name', flat=True)[0]
    except:
        groups = None
    if groups == 'instructor':

        modul = get_object_or_404(Module, pk=pk, course__owner=request.user)
        context = {
            'modul': modul,
            'course': modul.course
        }
        return render(request, 'dashboard/manage/module/module_detail.html', context)
    else:
        return redirect('course:homepage')


def update_modul(request, pk):
    try:
        groups = request.user.groups.values_list('name', flat=True)[0]
    except:
        groups = None
    if groups == 'instructor':

        modul = get_object_or_404(Module, pk=pk, course__owner=request.user)
        form = ModulForm(request.POST or None, instance=modul)

        if request.method == 'POST':
            if form.is_valid():
                form.save()
                return redirect('course:manage:detail-modul', pk=modul.id)

        context = {
            'modul': modul,
            'form': form,
            'course': modul.course
        }
        return render(request, 'dashboard/manage/module/modul_form.html', context)
    else:
        return redirect('course:homepage')


def module_form(request):
    try:
        groups = request.user.groups.values_list('name', flat=True)[0]
    except:
        groups = None

    if groups == 'instructor':
        form = ModulForm()
        context = {
            'form': form,
        }

        return render(request, 'dashboard/manage/module/modul_form.html', context)
    else:
        return redirect('course:homepage')


# module contents views

# create update content
class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    content = None
    template_name = 'dashboard/manage/content/content_form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(
            model, exclude=['owner', 'order', 'created', 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        try:
            groups = request.user.groups.values_list('name', flat=True)[0]
        except:
            groups = None
        if groups == 'instructor':
            self.module = get_object_or_404(Module,
                                            id=module_id,
                                            course__owner=request.user)
            self.model = self.get_model(model_name)

            if id:
                self.obj = get_object_or_404(self.model, id=id, owner=request.user)
                self.content = get_object_or_404(
                    Content, object_id=id, module__course__owner=self.request.user)
            return super().dispatch(request, module_id, model_name, id=None)
        else:
            return redirect('course:homepage')

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({
            'modul_id': module_id,
            'modul_name': model_name,
            'form': form,
            "object": self.obj,
            'content': self.content
        })

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                Content.objects.create(
                    module=self.module, item=obj
                )
            try:
                content = Content.objects.filter(
                    object_id=obj.id, module__course__owner=self.request.user).last()
            except Content.DoesNotExist:
                content = None
            return render(request, 'dashboard/manage/content/content_details.html',
                          context={'item': obj, 'module': self.module, 'content': content})

        return self.render_to_response(
            {'form': form,
             'object': self.obj}
        )


class ContentDeleteView(View):

    def dispatch(self, request, id, *args, **kwargs):
        try:
            groups = request.user.groups.values_list('name', flat=True)[0]
        except:
            groups = None
        if groups == 'instructor':
            return self.post(request, id)
        else:
            return redirect('course:homepage')

    def post(self, request, id):
        content = get_object_or_404(
            Content, id=id, module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return HttpResponse('')


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'dashboard/manage/module/content_list.html'

    def dispatch(self, request, module_id, *args, **kwargs):
        try:
            groups = request.user.groups.values_list('name', flat=True)[0]
        except:
            groups = None
        if groups == 'instructor':
            return self.get(request, module_id)
        else:
            return redirect('course:homepage')

    def get(self, request, module_id):
        module = get_object_or_404(Module,
                                   id=module_id,
                                   course__owner=request.user)

        return self.render_to_response({'module': module})


def content_detail(request, module_id, content_id, item_id):
    try:
        groups = request.user.groups.values_list('name', flat=True)[0]
    except:
        groups = None
    if groups == 'instructor':
        module = get_object_or_404(Module,
                                   id=module_id,
                                   course__owner=request.user)
        content = get_object_or_404(
            Content, id=content_id, module__course__owner=request.user)
        context = {
            'content': content,
            'module': module
        }
        return render(request, 'dashboard/manage/content/content_details.html', context=context)
    else:
        return redirect('course:homepage')


# group views

class GroupMixin(object):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(course__owner=self.request.user)


class OwnerGroupMixin(GroupMixin,
                      LoginRequiredMixin,
                      PermissionRequiredMixin):
    model = GroupCourse
    fields = ['title', 'start_date', 'end_date', 'time_start', 'time_end']


class GroupCourseCreateView(OwnerGroupMixin, TemplateResponseMixin, View):
    permission_required = ['courses.add_groupcourse',
                           'courses.delete_groupcourse', ]
    http_method_names = ['get', 'post', 'delete', 'put']
    course = None
    group = None

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.http_method_names:
            self.course = get_object_or_404(
                Course, id=kwargs['pk'], owner=request.user)
            if request.method.lower() == 'get':
                return self.get(request, kwargs['pk'])
            elif request.method.lower() == 'post':
                return self.post(request, kwargs['pk'])
            elif request.method.lower() == 'delete':
                return self.delete(request, pk=kwargs['pk'], slug=kwargs['slug'])

    def get(self, request, pk):
        form = GroupForm()
        context = {
            'form': form,
            'course': self.course
        }
        return render(request, 'dashboard/manage/group/group_form.html', context)

    def post(self, request, pk):
        form = GroupForm(request.POST or None)
        if form.is_valid():
            groupcourse = form.save(commit=False)
            groupcourse.course = self.course
            groupcourse.slug = f"{str(uuid.uuid4())}"
            groupcourse.save()
            return redirect('course:manage:detail_group', pk=self.course.id, slug=groupcourse.slug)
        else:
            return render(request, 'dashboard/manage/group/group_form.html',
                          context={'form': form, 'course': self.course})

    def delete(self, request, pk, slug):
        group = get_object_or_404(
            GroupCourse, slug=slug, course__owner=request.user)
        group.delete()
        return HttpResponse('')


@permission_required('courses.add_groupcourse')
def group_form(request, pk):
    form = GroupForm()
    course = get_object_or_404(Course, pk=pk)
    context = {
        'form': form,
        'course': course
    }
    return render(request, 'dashboard/manage/group/group_form.html', context)


@permission_required('courses.add_groupcourse')
def detail_groupcourse(request, pk, slug):
    # groupcourse=get_object_or_404(GroupCourse,slug=slug,course__id=course_id,course__owner=request.user)
    groupcourse = get_object_or_404(
        GroupCourse, slug=slug, course__id=pk, course__owner=request.user)
    context = {
        'group': groupcourse,
        'course': groupcourse.course
    }
    return render(request, 'dashboard/manage/group/group_detail.html', context=context)


@permission_required('courses.add_groupcourse')
def update_group(request, pk, slug):
    groupcourse = get_object_or_404(GroupCourse, slug=slug, course__id=pk)
    course = get_object_or_404(Course, pk=pk)
    form = GroupForm(request.POST or None, instance=groupcourse)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('course:manage:detail_group', pk=pk, slug=slug)
    context = {
        'form': form,
        'group': groupcourse,
        'course': course
    }
    return render(request, 'dashboard/manage/group/group_form.html', context)


class GroupCourseDetailViev(TemplateResponseMixin, View):
    http_method_names = ['get', 'post', 'delete']
    template_name = 'dashboard/manage/group/manage_group_detail.html'
    group = None

    def get(self, request, slug):
        self.group = get_object_or_404(GroupCourse, slug=slug, course__owner=request.user)
        schedules = self.group.modules.all()
        return self.render_to_response({
            'object': self.group,
            'schedules': schedules,
        })

    def post(self, request, slug):
        # list = []
        self.group = get_object_or_404(GroupCourse, slug=slug, course__owner=request.user)
        try:
            modules = self.group.course.modules.all()
        except:
            modules = None
        form = GroupSchedule(request.POST or None)
        if form.is_valid():
            obj = GroupCourse.objects.filter(slug=slug, course__owner=request.user)
            date = form.cleaned_data.get('start_date')
            week_days = form.cleaned_data.get('days_of_the_week')
            days = form.cleaned_data.get('days')

            x = 0
            while x != modules.count():
                if date.strftime('%w') in week_days and str(date) not in days:
                    if x == 0:
                        obj.update(
                            start_date=date
                        )

                    time = self.group.time_start
                    d = datetime.datetime(date.year, date.month, date.day, time.hour, time.minute, time.second)
                    self.group.modules.update_or_create(
                        module=modules[x],
                        date=d
                    )
                    x += 1
                else:
                    pass
                date += datetime.timedelta(days=1)
            date -= datetime.timedelta(days=1)
            obj.update(
                end_date=date
            )

        return redirect('course:manage:manage_group_detail', slug=self.group.slug)


def group_active(request, slug):
    g = get_object_or_404(GroupCourse, slug=slug)
    if request.method == 'POST':
        active = request.POST.get('active')
        if active:
            if g.modules and g.start_date and g.end_date:
                g.active = True
                g.save()
                return HttpResponse(
                    'checked'
                )
            return HttpResponse(None)
        else:
            g.active = False
            g.save()
            return HttpResponse(None)

    return HttpResponse('<input type="checkbox" hx-post="." hx-target="this" hx-trigger="click" value="check">')


def group_schedule_form(request, slug):
    form = GroupSchedule()
    return render(request, 'dashboard/manage/group/htmx_form/group_schedule_form.html',
                  context={'form': form, 'slug': slug})


class GroupCourseListView(PermissionRequiredMixin, TemplateResponseMixin, View):
    permission_required = 'courses.change_course'

    template_name = 'dashboard/manage/group/manage_group_list.html'
    group = None

    def dispatch(self, request, *args, **kwargs):
        self.group = GroupCourse.objects.filter(course__owner=request.user)
        return super(GroupCourseListView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        return self.render_to_response({
            'groups': self.group,
            'active': 'active'
        })


class GroupContentView(TemplateResponseMixin, View):
    template_name = 'dashboard/manage/group/htmx_form/group_content.html'
    group = None
    module = None

    def dispatch(self, request, *args, **kwargs):
        self.group = get_object_or_404(GroupCourse, slug=kwargs['slug'], course__owner=request.user)
        self.module = get_object_or_404(GroupModuleContent, id=kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.render_to_response({
            'group': self.group,
            'module': self.module,
            'group_m_id': self.module.id

        })


class GroupContentCreateUpdateView(TemplateResponseMixin, View):
    template_name = 'dashboard/manage/group/htmx_form/group_content_form.html'
    g_module = None
    model = None
    obj = None

    def dispatch(self, request, group_m_id, model_name, id=None, *args, **kwargs):
        self.g_module = get_object_or_404(GroupModuleContent, id=group_m_id, module__course__owner=request.user)
        self.model = self.get_model(model_name)

        if id:
            self.obj = get_object_or_404(self.model, id=id, owner=request.user)
        return super().dispatch(request, group_m_id, model_name, id=None, *args, **kwargs)

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file', 'zoom']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(
            model, exclude=['owner', 'order', 'created', 'updated'])
        return Form(*args, **kwargs)

    def get(self, request, group_m_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({
            'group_m_id': group_m_id,
            'model_name': model_name,
            'form': form,
            'object': self.obj
            # "object": self.obj
        })

    def post(self, request, group_m_id, model_name, id=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                GroupContents.objects.create(
                    module=self.g_module, item=obj
                )
            try:
                content = GroupContents.objects.get(object_id=obj.id)
            except GroupContents.DoesNotExist:
                content = None
            return render(request, 'dashboard/manage/group/htmx_form/group_content_detail.html', context={
                'item': obj,
                'group_m_id': group_m_id,
                'content': content

            })

        return self.render_to_response({
            'form': form,
            'object': self.obj
        })


def detail_group_content(request, group_m_id, item_id):
    try:
        obj = GroupContents.objects.get(object_id=item_id, module=group_m_id,
                                        module__module__course__owner=request.user)
    except GroupContents.DoesNotExist:
        obj = None
    context = {
        'item': obj.item,
        'group_m_id': group_m_id,
        'content': obj
    }
    return render(request, 'dashboard/manage/group/htmx_form/group_content_detail.html', context=context)


class GroupContentDeleteView(View):

    def post(self, request, group_m_id, item_id):
        content = get_object_or_404(
            GroupContents, id=item_id, module=group_m_id, module__module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return HttpResponse('')
