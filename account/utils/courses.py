from django.conf import settings
import base64

from account.models import Students
from courses.models import Transaction


def activate_course(user, course, group):
    std = Students.objects.get(user=user)
    course.students.add(std)
    group.students.add(std)


def generate_pay_url(course, group, student):
    transaction, _ = Transaction.objects.get_or_create(amount=int(course.price), group=group, student=student,
                                                       course=course, is_payed=False)

    params = f"m={settings.PAYME_MERCHANT_ID};" \
             f"ac.transaction={transaction.id};" \
             f"a={transaction.amount};" \
             f"c={settings.FRONTEND_DOMAIN}/students/courses/" \
             f"ct=3000"

    prod_url = "https://checkout.paycom.uz/"
    test_url = "https://test.paycom.uz/"

    url = test_url + base64.b64encode(bytes(params, 'utf-8')).decode("utf-8")
    return url
