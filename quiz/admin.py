from django.contrib import admin
from quiz.models import Quiz, Question, Answer, Sertificate, Result

# Register your models here.

admin.site.register(Answer)
admin.site.register(Question)
admin.site.register(Quiz)
admin.site.register(Sertificate)
admin.site.register(Result)
