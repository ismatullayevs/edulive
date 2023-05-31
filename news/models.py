from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse

from account.models import CustomUser

import email


# Create your models here.

class Comment(models.Model):
    author = models.CharField(max_length=50)
    content = models.TextField()

    # the required fields to enable a generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return self.author


class Article(models.Model):
    img = models.ImageField(blank=True, upload_to='news/%y%m/')
    title = models.CharField(max_length=255)
    subtitle = models.TextField(blank=True)
    body = RichTextUploadingField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
    )
    comments = GenericRelation(Comment)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', args=[str(self.id)])
