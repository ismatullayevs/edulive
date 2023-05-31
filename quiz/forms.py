from django import forms
from django.forms import inlineformset_factory, formset_factory
from django.utils.translation import gettext_lazy as _

from courses.models import Comments
from quiz.models import Quiz, Question, Answer


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = '__all__'


answer = inlineformset_factory(Question, Answer,
                               fields=['text', 'correct'],
                               min_num=2,
                               extra=4,
                               can_delete=False,
                               )

# class QuestionForm(forms.ModelForm):
#     quiz = forms.ModelChoiceField(queryset=Quiz.objects.all(), widget=forms.HiddenInput)
#     text = forms.CharField(label='test savol', widget=forms.Textarea(attrs={'rows': 4}))
#
#     class Meta:
#         model = Question
#         fields = '__all__'


ModuleFormSetAnswers = inlineformset_factory(Question, Answer,
                                             fields=['text', 'correct', ],
                                             extra=4,
                                             max_num=4,
                                             can_delete=False,
                                             widgets={
                                                 'correct': forms.RadioSelect(
                                                     attrs={'class': 'form-check-input', 'role': 'switch'}),
                                                 'text': forms.Textarea(attrs={'rows': 3})
                                             }
                                             )


class AnswerForm(forms.ModelForm):
    correct = forms.RadioSelect()
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, }))
    question = forms.ModelChoiceField(queryset=Question.objects.all(), widget=forms.HiddenInput)

    class Meta:
        model = Answer
        fields = '__all__'


# class AnswerFormset(forms.ModelForm):
#     correct = forms.ChoiceField(widget=forms.CheckboxInput)
#     text =
#     class Meta:
#         model = Answer
#         fields = ['text','correct']

class QuestionForm(forms.ModelForm):
    quiz = forms.ModelChoiceField(queryset=Quiz.objects.all(), widget=forms.HiddenInput)
    text = forms.CharField(label=_('Savol'), widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = Question
        fields = ['text', 'quiz']


# class QForm(forms.ModelForm):
#     quiz = forms.ModelChoiceField(queryset=Quiz.objects.all(), widget=forms.HiddenInput)
#     text = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'textarea form-control'}))
#
#     class Meta:
#         model = Question
#         fields = ['text', 'quiz']


answer_formset = inlineformset_factory(Question, Answer,
                                       extra=4,
                                       max_num=4,
                                       can_delete=False,
                                       fields=['text', 'correct'],
                                       widgets={
                                           'correct': forms.CheckboxInput(
                                               attrs={'class': 'checkboxinput form-check-input'}),
                                           'text': forms.Textarea(attrs={'rows': 3, 'class': 'textarea form-control'})})
