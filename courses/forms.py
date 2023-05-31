import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from courses.models import Course, Module, GroupCourse


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('subject', 'title', 'overview', 'img','price')
        widgets = {
            'img': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        img = cleaned_data.get('img')
        mb = img.size
        print(mb)
        if mb > 5096000:
            print('warning')
            self.add_error('img', _('Rasm hajmi 5MB dan katta'))


class ModulForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = (
            'title',
            'description',

        )


ModuleFormSet = inlineformset_factory(Course, Module,
                                      fields=['title', 'description'],
                                      min_num=2,
                                      extra=1,
                                      can_delete=True,
                                      )


class GroupForm(forms.ModelForm):
    class Meta:
        model = GroupCourse
        fields = (
            'title', 'time_start', 'time_end',
        )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'time_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'time_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
        }


class GroupSchedule(forms.Form):
    week_days = (
        ('1', 'dushanba'),
        ('2', 'seshanba'),
        ('3', 'chorshanba'),
        ('4', 'payshanba'),
        ('5', 'juma'),
        ('6', 'shanba'),
        ('0', 'yakshanba'),
    )

    days_out_off = [(datetime.date.today() + datetime.timedelta(i), datetime.date.today() + datetime.timedelta(i)) for i
                    in range(730)]

    days = forms.MultipleChoiceField(label='istisno kunlar(agar bo\'lsa)',
                                     help_text='2 va undan ortiq tanlash uchun ctrl + ni bosib tanlang',
                                     widget=forms.SelectMultiple(), choices=days_out_off, required=False)
    start_date = forms.DateField(label='Boshlash sanasi', widget=forms.DateInput(attrs={'type': 'date'}))
    days_of_the_week = forms.MultipleChoiceField(label='Hafta kunlari', widget=forms.CheckboxSelectMultiple(),
                                                 choices=week_days)
