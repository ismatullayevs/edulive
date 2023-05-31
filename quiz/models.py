import os
import random
from io import BytesIO

import uuid as uuid
from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File as F
from PIL import ImageDraw, Image as Img
from django.urls import reverse

from account.models import Students
from courses.fields import OrderField
from courses.models import Course


# Create your models here.
class Quiz(models.Model):
    DIFF_CHOICES = (
        ('easy', 'easy'),
        ('medium', 'medium'),
        ('hard', 'hard'),
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizs')
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    number_of_questions = models.IntegerField()
    score_to_pass = models.IntegerField(help_text="O'tish uchun eng past ball")
    time = models.IntegerField(help_text="test yechish uchun vaqt davomiyligi")
    created = models.DateTimeField(auto_now_add=True)
    difficulty = models.CharField(max_length=255, choices=DIFF_CHOICES)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.course}: {self.title}"

    def get_questions(self):
        questions = list(self.questions.all())
        random.shuffle(questions)
        return questions[:self.number_of_questions]


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    order = OrderField(blank=True, for_fields=['quiz'], null=True)

    # def __str__(self):
    #     return f"{self.text}"

    def get_answers(self):
        answers = list(self.answers.all())
        random.shuffle(answers)
        return answers

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['created']


class Answer(models.Model):
    text = models.TextField(blank=True, null=True)
    correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    created = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    order = OrderField(blank=True, for_fields=['question'], null=True)

    def __str__(self):
        return f'savol: {self.question.text} - javob: {self.correct}'

    class Meta:
        ordering = ['-created']


class Result(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='result', related_query_name='result')
    student = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='result')
    score = models.FloatField()
    attempts = models.IntegerField(verbose_name='urinishlar soni', help_text='Urinishlar soni', default=1)

    def __str__(self):
        return f"{self.student}: result {self.score}"

    def result(self):
        return f"{self.student}: result {self.score}"


class Sertificate(models.Model):
    def content_image_name(instance, filename):
        return '/'.join([f'{instance.course}', str(instance.student), filename])

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sertificate')
    student = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='sertificate',
                                related_query_name='sertificate')
    qr_photo = models.ImageField(editable=False, upload_to=content_image_name, blank=True)
    created = models.DateField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('account:sertificate', kwargs={'uuid': self.uuid})

    def save(self, *args, **kwargs):
        try:
            if len(self.qr_photo) > 0:
                os.remove(self.qr_photo.path)
        except:
            pass

        qrcode_img = qrcode.make(f"{self.get_absolute_url()}")
        canvas = Img.new('RGB', (450, 450), 'white')
        draw = ImageDraw.Draw(canvas)
        canvas.paste(qrcode_img)
        fname = f"{str(self.student).strip(' ')}" + '.png'
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        self.qr_photo.save(fname, F(buffer), save=False)
        canvas.close()
        super().save(*args, **kwargs)
