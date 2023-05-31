import uuid
from datetime import date

from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from embed_video.fields import EmbedVideoField
from slugify import slugify

from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager

from courses.fields import OrderField
from courses.managers import CouseManager
from account.models import CustomUser, Students
from django.utils.translation import gettext_lazy as _


class Subject(MPTTModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['title']

    def __str__(self):
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(
        CustomUser, related_name='courses_created', related_query_name='course_created', on_delete=models.CASCADE)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name='courses', related_query_name='courses',
        verbose_name='kurs turi')
    title = models.CharField(verbose_name='kursning nomi', max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    overview = models.TextField(verbose_name='kurs haqida qisqacha ma\'lumot')
    created = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(Students,
                                      related_name='courses_joined', related_query_name='courses_joined', blank=True)
    img = models.ImageField(upload_to='images/courses/', blank=True)
    active = models.BooleanField(default=False)
    price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    tags = TaggableManager(blank=True)

    # actived = CouseManager()
    # objects = models.Manager()

    def __str__(self):
        return self.title

    def sum_std(self):
        return self.students.count()

    def get_absolute_url(self):
        return reverse('course:course_detail', kwargs={'slug': self.slug})

    class Meta:
        ordering = ('-created',)


class GroupCourse(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='groupcourse')
    created_date = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(
        Students, related_name='groupcourse', related_query_name='groupcourse', blank=True)
    slug = models.SlugField(unique=True, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    time_start = models.TimeField(blank=True, null=True)
    time_end = models.TimeField(blank=True, null=True)
    notice = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=False)
    modules = GenericRelation('GroupModuleContent', related_query_name='groupcourse')

    def __str__(self):
        return f"{self.title}({str(self.time_start)[0:5]} ~ {str(self.time_end)[0:5]}(uzb))"

    def time(self):
        return f"({str(self.time_start)[0:5]} ~ {str(self.time_end)[0:5]})"

    def get_absolute_url(self):
        return reverse('detail_group', kwargs={'pk': self.pk})

    def std_count(self):
        return f"{self.students.count()}"

    def total(self):
        return self.modules.all()

    def complate_modules(self):
        return self.modules.filter(date__lt=date.today())

    def progress(self):
        if self.total().count() > 0:
            return f"{int((self.complate_modules().count() / self.total().count()) * 100)}"
        else:
            return 0

    # class Meta:
    #     ordering = ['-created_date']

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(f"{str(uuid.uuid4())}")
        return super().save(*args, **kwargs)


class Module(MPTTModel):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField('mavzu', max_length=200)
    description = models.TextField("mavzu bo'yicha malumot", blank=True)
    order = OrderField(blank=True, for_fields=['course'], null=True)

    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return f'{self.order}. {self.title}'

    class Meta:
        ordering = ['order']


class Content(models.Model):
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name='contents')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     limit_choices_to={'model_in': (
                                         'text',
                                         'video',
                                         'image',
                                         'file',
                                     )}
                                     )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'], null=True)

    class Meta:
        ordering = ['order']


class ItemBase(models.Model):
    owner = models.ForeignKey(
        CustomUser, related_name='%(class)s_related', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Sarlavha', max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.title}"

    def render(self):
        return render_to_string(
            f'students/{self._meta.model_name}.html', {'item': self})


class Text(ItemBase):
    content = models.TextField(verbose_name=_('Text'))


class File(ItemBase):
    file = models.FileField(verbose_name=_('File'), upload_to='files')


class Image(ItemBase):
    image = models.ImageField(verbose_name=_('Rasm'), upload_to='images')


class Video(ItemBase):
    url = EmbedVideoField(verbose_name=_('Video manzil'))
    # url = models.URLField(verbose_name=_('Video manzil'))


class Zoom(ItemBase):
    url = models.URLField(verbose_name=_('Url zoom'))


class GroupModuleContent(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='groupmodule', null=True)
    date = models.DateTimeField(blank=True)
    comments = GenericRelation('Comments', null=True, related_query_name='group_module')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')

    order = OrderField(blank=True, for_fields=['module'], null=True)

    def __str__(self):
        return f"{self.module.title}"

    def date_format(self):
        day = self.date.today()
        return day


class GroupContents(models.Model):
    module = models.ForeignKey(GroupModuleContent, on_delete=models.CASCADE, related_name='groupcontents')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     limit_choices_to={'model_in': (
                                         'zoom',
                                         'text',
                                         'video',
                                         'image',
                                         'file',
                                     )}
                                     )

    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'], null=True)


class Comments(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comment')
    content = models.TextField()
    reply = models.ForeignKey('Comments', on_delete=models.CASCADE, blank=True, null=True, related_name='replies')
    timestamp = models.DateTimeField(auto_now_add=True)

    # the required fields to enable a generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return str(self.content)

    class Meta:
        ordering = ('-timestamp',)


class Transaction(models.Model):
    course = models.ForeignKey('courses.Course', models.PROTECT)
    group = models.ForeignKey('courses.GroupCourse', models.PROTECT)
    student = models.ForeignKey('account.Students', models.PROTECT)

    amount = models.IntegerField()  # sum
    is_payed = models.BooleanField(default=False)
    payed_at = models.DateTimeField(null=True, blank=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    state = models.IntegerField(default=0)
    canceled_at = models.DateTimeField(null=True, blank=True)

    payme_id = models.CharField(null=True, blank=True, max_length=255)
    payme_created_at = models.DateTimeField(null=True, blank=True)
    reason = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
