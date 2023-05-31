from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
import base64

from account.utils.payment import check_perform_transaction, create_transaction, check_transaction, perform_transaction
from account.utils.payment import cancel_transaction
from courses.models import Transaction


class PaymeView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        method = request.data.get('method')
        authorization = request.headers.get('Authorization')
        auth_token = base64.b64encode(bytes('Paycom:' + settings.PAYME_KEY, 'utf-8')).decode("utf-8")
        params = request.data.get('params', {})

        not_found_error = {
            'error': {
                'code': -31050,
                'message': {
                    'ru': 'Транзакция не найдена.',
                    'uz': 'To\'lov topilmadi',
                    'en': 'Transaction not found'
                },
            },
            'id': request.data.get('id')
        }

        transaction = None
        ip = request.META.get('HTTP_X_FORWARDED_FOR')

        if ip not in ['195.158.31.134', '195.158.31.10']:
            return Response({'message': 'Access Denied'})

        if not authorization or authorization.split()[1] != auth_token:
            return Response({
                'id': request.data.get('id'),
                'error': {'code': -32504, 'message': 'Unauthorized'}
            })

        if params.get('account', {}).get('transaction'):
            transaction = Transaction.objects.filter(id=params.get('account').get('transaction'))

            if not transaction.exists():
                return Response(not_found_error)

        elif params.get('id'):
            transaction = Transaction.objects.filter(payme_id=params.get('id'))

            if not transaction.exists():
                not_found_error['error']['code'] = -31003
                return Response(not_found_error)

        transaction = transaction.first()
        response = {}

        if method == 'CheckPerformTransaction':
            response = check_perform_transaction(request.data, transaction)

        if method == 'CreateTransaction':
            response = create_transaction(request.data, transaction)
            transaction.save()

        if method == 'CheckTransaction':
            response = check_transaction(transaction)
            transaction.save()

        if method == 'PerformTransaction':
            response = perform_transaction(transaction)
            transaction.save()

        if method == 'CancelTransaction':
            response = cancel_transaction(request.data, transaction)
            transaction.save()

        return Response(response)
