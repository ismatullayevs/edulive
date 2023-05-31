from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from account.models import CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()


class UserNamePhoneAuthBackend(ModelBackend):
    """UserName or Phone Authentication Backend.

    Allows user sign in with email or phone then check password is valid
    or not and return user else return none
    """

    def authenticate(self, request, username_or_phone=None, password=None, role=None):
        try:
            user = User.objects.get(
                (Q(username=username_or_phone) | Q(phone_number=username_or_phone)))
        except ObjectDoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
            else:
                return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return None
