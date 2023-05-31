import os
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.views.generic.base import TemplateResponseMixin, View

from account.models import Students
from courses.models import Course, GroupCourse
from quiz.forms import QuizForm, QuestionForm, answer_formset
from quiz.models import Quiz, Question, Result, Answer, Sertificate


class QuizListView(ListView):
    template_name = 'dashboard/quiz/quiz.html'
    context_object_name = 'quiz_list'
    model = Quiz

    def dispatch(self, request, *args, **kwargs):
        try:
            groups = request.user.groups.values_list('name', flat=True)[0]
        except:
            groups = None

        if groups == 'instructor':
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('course:homepage')

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(course__owner=self.request.user)


class QuizCreateUpdateview(TemplateResponseMixin, View):
    template_name = 'dashboard/quiz/quiz_form.html'
    obj = None
    course = None
    http_method_names = ['get', 'post', 'delete']

    def dispatch(self, request, id=None, *args, **kwargs):

        try:
            groups = request.user.groups.values_list('name', flat=True)[0]
        except:
            groups = None

        if groups == 'instructor':
            self.course = Course.objects.filter(owner=request.user)
            if id:
                self.obj = get_object_or_404(Quiz, pk=id, course__owner=request.user)
            if request.method.lower() == 'delete':
                return self.delete(request, id)

            return super(QuizCreateUpdateview, self).dispatch(request, id, *args, **kwargs)
        else:
            return redirect('course:homepage')

    def get(self, request, id=None):
        form = QuizForm(instance=self.obj)
        form.fields['course'].queryset = self.course
        return self.render_to_response({'form': form, 'object': self.obj})

    def post(self, request, id=None):
        form = QuizForm(request.POST, instance=self.obj)
        print(self.obj)
        form.fields['course'].queryset = self.course
        if form.is_valid():
            self.obj = form.save()
            return redirect('quiz:detail_quiz', pk=self.obj.pk)
        return self.render_to_response({'form': form})

    def delete(self, request, id):
        self.obj.delete()
        return HttpResponse('')


def quiz_active(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)

    if request.method == 'POST':
        active = request.POST.get('active')
        print(active)
        if active:
            quiz.active = True
            quiz.save()
            return HttpResponse('checked')
        else:
            quiz.active = False
            quiz.save()
            return HttpResponse(None)

    return HttpResponse('<input type="checkbox" hx-post="." hx-target="this" hx-trigger="click" value="check">')


def detail_course_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, course__owner=request.user)
    context = {'object': quiz}
    return render(request, 'dashboard/quiz/course_quiz_detail.html', context)


def quiz_form(request, id=None):
    try:
        obj = Quiz.objects.get(pk=id, course__owner=request.user)
    except:
        obj = None
    form = QuizForm(instance=obj)
    form.fields['course'].queryset = Course.objects.filter(owner=request.user)
    contex = {'form': form}
    return render(request, 'dashboard/quiz/quiz_form.html', context=contex)


class AddQuestionsView(TemplateResponseMixin, View):
    template_name = 'dashboard/quiz/question_list.html'

    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id, course__owner=request.user)

        return self.render_to_response({
            'questions': quiz.questions.all(),
            'quiz': quiz,
        })

    def post(self, request, quiz_id):
        form = QuestionForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            obj = form.save()
            return render(request, 'dashboard/quiz/questions_detail.html', {'object': obj, 'quiz_id': quiz_id})


def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk, quiz__course__owner=request.user)
    context = {
        'object': question
    }
    return render(request, 'dashboard/quiz/questions_detail.html', context)


def question_form(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, course__owner=request.user)
    print(quiz)
    form = QuestionForm(initial={'quiz': quiz})
    formset = answer_formset()

    if request.method == 'POST':

        form = QuestionForm(request.POST)
        formset = answer_formset(request.POST or None)
        print(form)
        if all([form.is_valid(), formset.is_valid()]):
            print('form is valid')
            question = form.save(commit=False)
            quiz_obj = type(form.cleaned_data['quiz'])
            print(quiz_obj)
            question.save()
            answers = formset.save(commit=False)
            print(question)
            for answer in answers:
                answer.question = question
                answer.save()
            print('post save boldi')
            return render(request, 'dashboard/manage/detail_question.html', {'question': question})

    return render(request, 'dashboard/manage/question_form.html',
                  {'formset': formset, 'form': form, 'quiz_id': quiz_id})


def update_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id, quiz__course__owner=request.user)

    formset = answer_formset(instance=question)
    form = QuestionForm(instance=question)
    print(formset)

    if request.method.lower() == 'post':
        form = QuestionForm(request.POST, instance=question)
        formset = answer_formset(request.POST, instance=question)
        print(formset)
        print('form=', form.is_valid(), 'formset=', formset.is_valid())
        print(formset.errors)
        if all([form.is_valid(), formset.is_valid()]):
            question = form.save(commit=False)
            question.save()
            answers = formset.save(commit=False)
            for answer in answers:
                answer.question = question
                answer.save()
            # return HttpResponse('')
            return render(request, 'dashboard/manage/detail_question.html', {'question': question})
    context = {
        'formset': formset,
        'form': form,
        'quiz_id': question.quiz.id,
        'question_id': question_id
    }

    return render(request, 'dashboard/manage/question_update_form.html', context)


def delete_question(request, question_id):
    try:
        groups = request.user.groups.values_list('name', flat=True)[0]
    except:
        groups = None
    if groups == 'instructor':
        question = get_object_or_404(Question, pk=question_id, quiz__course__owner=request.user)
        question.delete()
        return HttpResponse('')


# student quiz views
class StudentQuizListView(ListView):
    model = Quiz
    template_name = 'students/quiz/quiz_list.html'
    quiz = None

    def get_queryset(self):
        quiz_list = []
        try:
            group = GroupCourse.objects.filter(end_date__gte=datetime.now())
            if group:
                for g in group:
                    quiz = g.course.quizs.all().first()
                    print(g.course.quizs.all())
                    if quiz is not None:
                        quiz_list.append(quiz)
        except:
            pass

        print(quiz_list)
        return quiz_list


def quiz_view(request, pk):
    quiz = Quiz.objects.get(pk=pk)
    try:
        r = Result.objects.get(quiz=quiz, student__user=request.user)
        if r.score >= quiz.score_to_pass:
            return redirect('quiz:student_quiz_list')
    except:
        pass

    return render(request, 'students/quiz/quiz_detail.html', context={'object': quiz})
    # try:
    #     result = Result.objects.get(student__user=request.user, quiz=quiz)
    # except:
    #     result = None
    # if not result:
    #     quiz = Quiz.objects.get(pk=pk)
    #     return render(request, 'students/dashboard/quiz/quiz_detail.html', context={'object': quiz})
    # else:
    #     return redirect('student_quiz_list')


def quiz_data_view(request, pk):
    quiz = Quiz.objects.get(pk=pk)
    # try:
    #     result = Result.objects.get(student__user=request.user, quiz=quiz)
    # except:
    #     result = None
    # if not result:
    quiz = Quiz.objects.get(pk=pk)
    questions = []
    # result = quiz.result.filter(student=request.user)
    # if result:
    #     print('bu user test yechgan')
    # else:
    #     print('user test hali yechmagan')
    for q in quiz.get_questions():
        answers = []
        for a in q.get_answers():
            answers.append(a.text)
        questions.append({str(q): answers})
    return JsonResponse({
        'data': questions,
        'time': quiz.time,
    })


def save_quiz_view(request, pk):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        questions = []
        data = request.POST
        data_ = dict(data.lists())
        print(data_)
        data_.pop('csrfmiddlewaretoken')
        print(data_)

        for k in data_.keys():
            question = Question.objects.get(text=k)
            questions.append(question)
        print('----------------', len(questions), '----------------')
        user = Students.objects.get(user=request.user)
        print(user)
        quiz = Quiz.objects.get(pk=pk)

        score = 0
        # multipler = 100 / quiz.number_of_questions
        multipler = 100 / len(questions)
        results = []
        correct_answer = None

        for q in questions:
            a_selected = request.POST.get(str(q))
            if a_selected != '':
                question_answer = Answer.objects.filter(question=q)
                for a in question_answer:
                    if a_selected == a.text:
                        if a.correct:
                            score += 1
                            correct_answer = a.text
                    else:
                        if a.correct:
                            correct_answer = a.text
                results.append({str(q): {'correct_answer': correct_answer, 'answered': a_selected}})
            else:
                results.append({str(q): 'not answered'})
        score_ = score * multipler
        print(score_)
        # Result.objects.create(
        #     quiz=quiz, student=user, score=score_,
        # )
        try:
            obj = Result.objects.get(quiz=quiz, student=user)
            obj.attempts += 1
            obj.score = score_
            obj.save()
            print('update ga keldi va topdi')
        except Result.DoesNotExist:
            obj = Result.objects.create(
                quiz=quiz, student=user, score=score_, attempts=1
            )
            obj.save()
            print('topolmadi', obj, 'manabuni saxranit qildi')
        # obj, created = Result.objects.update_or_create(
        #     quiz=quiz, student=user, defaults={'score':score_}
        # )
        # obj.score = score_
        # obj.attempts += 1
        # obj.save()

        if score_ >= quiz.score_to_pass:
            obj = Sertificate.objects.create(
                course=quiz.course,
                student=user,
            )
            obj.save()
            print('sertificat saqlandi --------------------')
            return JsonResponse({'passed': True, 'score': score_, 'results': results})
        else:
            return JsonResponse({'passed': False, 'score': score_, 'results': results})
