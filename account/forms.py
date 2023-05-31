from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from account.models import CustomUser, Students
from django.utils.translation import gettext_lazy as _

from courses.models import Course, GroupCourse, Comments
from .models import CustomUser
from django.core.cache import cache
import re

from django.core.exceptions import ValidationError


class RegisterUserForm(UserCreationForm):
    full_name = forms.CharField()

    phone_number = forms.CharField()

    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'username', 'phone_number', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)

        self.fields['full_name'] = forms.CharField(
            label=_('Familya Ism Sharif'), widget=forms.TextInput(attrs={'type': 'text', 'class': 'input100'})

        )

        self.fields['username'] = forms.CharField(
            label=_('Login'), widget=forms.TextInput(attrs={'type': 'text', 'class': 'input100'})

        )

        self.fields['email'] = forms.EmailField(label=_('Email'),
                                                widget=forms.TextInput(attrs={'type': 'text', 'class': 'input100'}))

        self.fields['phone_number'] = forms.CharField(label=_('Telefon Raqam'), widget=forms.NumberInput(
            attrs={'data-format': "+(*****) ***-**-**", "data-mask": "+(998__) __-__-__", 'type': 'tel',
                   'class': 'input100'}))

        self.fields['password1'] = forms.CharField(label=_('Parol'),
                                                   widget=forms.TextInput(
                                                       attrs={'type': 'password', 'class': 'input100'}))
        self.fields['password2'] = forms.CharField(
            label=_('Parolni qaytadan kiriting'),
            widget=forms.TextInput(attrs={'type': 'password', 'class': 'input100'})

        )

    def clean_phone_number(self):
        data = self.cleaned_data['phone_number']
        phone = re.findall('[0-9]+', data)
        if CustomUser.objects.filter(phone_number=''.join(phone)).exists():
            raise forms.ValidationError(_('Bu raqam allaqachon mavjud'))
        return ''.join(phone)

    def clean_email(self):
        data = self.cleaned_data['email']
        if CustomUser.objects.filter(email=data).exists():
            raise forms.ValidationError(_('Bu electron pochta ro\'xatdan o\'tgan'))
        return data

    def clean_username(self):
        data = self.cleaned_data['username']
        if CustomUser.objects.filter(username=data).exists():
            raise forms.ValidationError(_('Bu foydalanuvchi ro\'yxatdan o\'tgan'))
        return data.lower()

    def clean_full_name(self):
        data = self.cleaned_data['full_name']
        list_data = data.split(' ')
        if len(list_data) == 3:
            data = list(map(lambda s: str(s).capitalize(), list_data))
        elif len(list_data) == 4:
            data = list(map(lambda s: str(s).capitalize(), list_data[:3]))
            data[2] = data[2] + ' ' + list_data[3].lower()
        elif len(list_data) < 3 or len(list_data) > 4:
            raise forms.ValidationError(_("Ism Familya Sharif ni to'liq kiriting"))

        return ' '.join(data)

    def save(self, commit=True):
        instance = super().save(commit=False)
        cd = self.cleaned_data
        full_name = tuple(str(cd['full_name']).split(' '))
        last_name = full_name[0]
        first_name = full_name[1]
        fathers_name = ' '.join(full_name[2:])
        #(last_name, first_name, fathers_name) = full_name
        instance.last_name = last_name
        instance.first_name = first_name
        instance.father_name = fathers_name
        if commit:
            instance.save()
        return instance


class VerifyForm(forms.Form):
    code = forms.CharField(label=_('Verifikatsiya raqami'), widget=forms.TextInput(attrs={'class': 'input100'}))

    def clean_code(self):
        data = self.cleaned_data['code']

        if data.isdigit() and len(data) == 5:
            data = int(data)
        else:
            raise forms.ValidationError(_('tasdiqlash raqami faqat 5 ta raqamdan iborat'))
        return data


class LoginForm(forms.Form):
    username_or_phone = forms.CharField(label=_('login yoki parol'),
                                        widget=forms.TextInput(attrs={'class': 'input100'}))
    password = forms.CharField(label=_('Parol'),
                               widget=forms.PasswordInput(attrs={'class': 'input100'}))


class UpdateFormUser(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'father_name', 'phone_number', 'email', 'profile_image')

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control', 'type': 'text'}),

            'phone_number': forms.TextInput(
                attrs={'class': 'form-control', 'type': 'text', "placeholder": '9989xxyyyzzzz'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'type': 'email'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_phone_number(self):
        data = self.cleaned_data['phone_number']
        print(type(data))
        if len(data) == 12 and str(data).isdigit():
            return data
        else:
            raise forms.ValidationError(_("Raqam no'to'gri kiritildi"))


# student block

class CourseEnrollForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all(),
                                    widget=forms.HiddenInput)
    group = forms.ModelChoiceField(queryset=GroupCourse.objects.none(), label='bo\'sh vaqtingizga mos guruhni tanlang:')

    def __init__(self, course=None, r_user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if r_user is None:
            self.fields['pasport'] = forms.FileField(label=_('Pasport rasmi'),
                                                     help_text=_('[jpg, jpg, png, pdf] maxsimal 5MB '),
                                                     widget=forms.FileInput(attrs={
                                                         'class': 'form-control fn-size mb-3'
                                                     }))
            self.fields['selfi_pasport'] = forms.FileField(label=_('Pasport bilan selfi'),
                                                           help_text=_('[jpg, jpg, png, pdf] maxsimal 5MB '),
                                                           widget=forms.FileInput(attrs={
                                                               'class': 'form-control fn-size mb-3'
                                                           }))
            self.fields['date_of_birth'] = forms.DateField(label=_("Tug'ulgan kun"), widget=forms.DateInput(attrs={
                'class': 'form-control fn-size mb-3',
                'type': 'date'
            }))

        if course:
            self.fields['group'].queryset = GroupCourse.objects.filter(
                course=course, active=True)
        else:
            self.fields['group'].queryset = GroupCourse.objects.all()

    class Meta:
        fields = ['__all__']

    def clean(self):
        try:
            url = self.cleaned_data['pasport']
            print(url)
            valid_extensions = ['jpg', 'jpeg', 'png', 'pdf']
            extension = str(url).rsplit('.', 1)[1].lower()
            if extension not in valid_extensions:
                self.add_error('pasport', _("Rasm kengaytmasi to'g'ri kelmadi"))

        except:
            pass


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('content',)


class StudentUpdateForm(forms.ModelForm):
    class Meta:
        model = Students
        exclude = ['user']
