from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordContextMixin, PasswordResetView, INTERNAL_RESET_SESSION_TOKEN
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.shortcuts import render, redirect, resolve_url
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, UpdateView, TemplateView

from account.forms import RegisterUserForm, VerifyForm, LoginForm, UpdateFormUser
from django.contrib import messages

from account.models import CustomUser
from account.utils.otp_phone import OTP

from django.http import JsonResponse, HttpResponseRedirect
from datetime import datetime
from django.core.cache import cache
from datetime import datetime
from account.tasks import send_sms
from django.core.mail import send_mail

from django.utils.translation import gettext_lazy as _

from django.conf import settings
from get_sms import Getsms
UserModel = get_user_model()

def register(request):
    if request.user.is_authenticated:
        return redirect('course:homepage')
    form = RegisterUserForm()
    if request.method.lower() == 'get':
        request.session['date'] = str(datetime.now())
        cache_key = f"user_{request.session.session_key}"
        cache_form = cache.get(cache_key, version=1)
        cache_code = cache.get(cache_key, version=2)
        cache_count = cache.get(cache_key, version=3)
        print(cache_code)
    if request.method.lower() == 'post':
        cache_key = f"user_{request.session.session_key}"
	

#print(cache.get(cache_key, version=1), cache.get(cache_key, version=2)
        try:
            cache.delete(cache_key, version=1)
            cache.delete(cache_key, version=2)
            cache.delete(cache_key, version=3)
        except:
            pass
	#print(cache.get(cache_key, version=1)
        form = RegisterUserForm(request.POST)
        print(form.is_valid())
        if form.is_valid():

            data = {
                'username': form.cleaned_data['username'],
                'phone_number': form.cleaned_data['phone_number'],
                'full_name': form.cleaned_data['full_name'],
                'email': form.cleaned_data['email'],
                'password1': form.cleaned_data['password1'],
                'password2': form.cleaned_data['password2']
            }
            otp = OTP(cache_key, data)
            print(otp,'===============================================================================')
            phone = form.cleaned_data['phone_number']
            login = 'Stable'
            password = '51v4N0y4R3N5rbcy122c'
            message = Getsms(login=login, password=password)
            result = message.send_message(
                phone_numbers=[phone],
                text=f"sizning verifikatsiya kodingiz {otp.get_otp}"
                    )
            print(result)	   
 #print(result)
            # send_sms.delay(phone, str(otp))
            return redirect('account:verify')
        else:
            return render(request, 'account/registration/signup.html', {'forms': form})

    context = {
        'forms': form
    }
    return render(request, 'account/registration/signup.html', context=context)

# verify view
def verify(request):
    if request.user.is_authenticated:
        return redirect('course:homepage')
    cache_key = f'user_{request.session.session_key}'
    form = VerifyForm()

    cache_form = cache.get(cache_key, version=1)
    cache_code = cache.get(cache_key, version=2)
    cache_count = cache.get(cache_key, version=3)

    print(cache_form, cache_code, cache_count)
    if cache_form is None:
        return redirect('account:sign_up')
    if request.method.lower() == 'post':
        form = VerifyForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data['code']
            print(code)
            if otp:
                if int(code) == int(cache_code['code']):
                    # cachedan formani oladi
                    form = cache.get(cache_key, version=1)
                    user_form = RegisterUserForm(form)
                    if user_form.is_valid():
                        user = user_form.save()
                        messages.success(request, f'{user} foydalanuchi muvaffaqqiyatli ro\'yxatga olindi')
                        return redirect('account:log_in')

                else:
                    messages.warning(request, 'verifikatsiya kodi notogri ')
            context = {
                'form': form,
                'phone': cache_form['phone_number']
            }

            return render(request, 'account/registration/verify.html', context)

    context = {
        'form': form,
        'phone': cache_form['phone_number']
    }

    return render(request, 'account/registration/verify.html', context=context)


# resend otp code view
def otp(request):
    if request.user.is_authenticated:
        return redirect('course:homepage')

    cache_key = f"user_{request.session.session_key}"
    otp = OTP(cache_key)

    otp.resend

#    send_email.delay('tanknarziyev@gmail.com', str(otp))

    # sms sender
    # send_sms.delay(phone, str(otp))

    if otp.get_otp is not None:
        code = otp.get_otp
        count = otp.count
    return JsonResponse({'code': code, 'count': count}, status=200)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('course:homepage')
    form = LoginForm()

    if request.method.lower() == 'post':
        print('postga keldi')
        form = LoginForm(request.POST)
        if form.is_valid():
            print('valid boldi')
            cd = form.cleaned_data
            username_or_phone = cd['username_or_phone']
            password = cd['password']
            user = authenticate(username_or_phone=username_or_phone, password=password)
            if user:
                print('user topildi')
                login(request, user)
                return redirect('course:homepage')
            else:
                print('messagega keldi')
                messages.warning(request, _('login yoki parol noto\'g\'ri'))

    return render(request, 'account/registration/login.html', {'form': form})


def log_out(request):
    logout(request)
    return redirect('account:log_in')


def user_update_view(request):
    try:
        groups = request.user.groups.values_list('name', flat=True)[0]
    except:
        groups = None
    if groups == 'instructor':
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
        return render(request, 'dashboard/manage/profile_edit/profile_edit_teacher.html', context)
    else:
        return redirect('course:homepage')


# change password

class PasswordChangeView(PasswordContextMixin, FormView):
    form_class = PasswordChangeForm
    template_name = 'account/change/change_password.html'
    title = _('Password change')

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, 'Parol o\'zgartirlidi')
        return self.render_to_response(self.get_context_data(form_change=form, active=True))

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return self.render_to_response(self.get_context_data(form_change=form, active=True))


# password change done

class PasswordChangeDoneView(PasswordContextMixin, TemplateView):
    template_name = "registration/password_change_done.html"
    title = _("Password change successful")

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        try:
            groups = self.request.user.groups.values_list('name', flat=True)[0]
        except:
            groups = None
        if groups == 'instructor':
            return super().dispatch(*args, **kwargs)
        else:
            redirect('course:homepage')


# password reset done view
class PasswordResetDoneView(PasswordContextMixin, TemplateView):
    template_name = "registration/password_reset_done.html"
    title = _("Password reset sent")


# reset password
class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'account/change/reset_password.html'
    email_template_name = 'account/change/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject'
    success_message = "We've emailed you instructions for settings your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('course:homepage')


class PasswordResetConfirmView(PasswordContextMixin, FormView):
    form_class = SetPasswordForm
    post_reset_login = False
    post_reset_login_backend = None
    reset_url_token = "set-password"
    success_url = reverse_lazy("account:password_reset_complete")
    template_name = "registration/password_reset_confirm.html"
    title = _("Enter new password")
    token_generator = default_token_generator

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        if "uidb64" not in kwargs or "token" not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'uidb64' and 'token' parameters."
            )

        self.validlink = False
        self.user = self.get_user(kwargs["uidb64"])

        if self.user is not None:
            token = kwargs["token"]
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(
                        token, self.reset_url_token
                    )
                    return HttpResponseRedirect(redirect_url)

        # Display the "Password reset unsuccessful" page.
        return self.render_to_response(self.get_context_data())

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (
                TypeError,
                ValueError,
                OverflowError,
                UserModel.DoesNotExist,
                ValidationError,
        ):
            user = None
        return user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        if self.post_reset_login:
            auth_login(self.request, user, self.post_reset_login_backend)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context["validlink"] = True
        else:
            context.update(
                {
                    "form": None,
                    "title": _("Password reset unsuccessful"),
                    "validlink": False,
                }
            )
        return context


class PasswordResetCompleteView(PasswordContextMixin, TemplateView):
    template_name = "registration/password_reset_complete.html"
    title = _("Password reset complete")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["login_url"] = resolve_url(settings.LOGIN_URL)
        return context
