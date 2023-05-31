from datetime import datetime, timedelta


def check_perform_transaction(data, transaction):
    params = data.get('params', {})

    if transaction.state < 0:
        return {
            'error': {
                'code': -31050,
                'message': {
                    'ru': 'Заказ недоступен для оплаты',
                    'uz': 'Buyurtma to\'lov uchun mavjud emas',
                    'en': 'The order is not available for payment'
                },
            },
            'id': data.get('id')
        }

    if transaction.amount != params.get('amount'):
        return {
            'error': {
                'code': -31001,
                'message': {
                    'ru': 'Суммы не совпадают',
                    'uz': 'Narxlar mos kelmaydi',
                    'en': 'The amounts do not match'
                },
            },
            'id': data.get('id')
        }

    return {'result': {'allow': True}}


def create_transaction(data, transaction):
    params = data.get('params', {})

    if params.get('amount') != transaction.amount:
        return {
            'error': {
                'code': -31001,
                'message': {
                    'ru': 'Суммы не совпадают',
                    'uz': 'Narxlar mos kelmaydi',
                    'en': 'The amounts do not match'
                },
            },
            'id': data.get('id')
        }

    transaction.payme_created_at = datetime.fromtimestamp(params.get('time') / 1000)

    if not transaction.payme_id:
        res = check_perform_transaction(data, transaction)

        if res.get('error'):
            return res

        transaction.state = 1
        transaction.payme_id = params.get('id')

        return {
            'result': {
                'state': transaction.state,
                'create_time': int(transaction.created_at.timestamp() * 1000),
                'transaction': transaction.token
            }
        }

    if params.get('id') != transaction.payme_id:
        return {
            'error': {
                'code': -31050,
                'message': 'Для этого заказа существует другие активные/завершение транзакции',
            },
            'id': data.get('id')
        }

    now = datetime.now(transaction.payme_created_at.tzinfo) + timedelta(hours=5)
    transaction_expires_at = transaction.payme_created_at + timedelta(hours=12)

    if transaction_expires_at < now:
        transaction.is_active = False
        transaction.state = -1
        transaction.reason = 4

    if transaction.state != 1 or transaction_expires_at < now:
        return {
            'code': -31008,
            'message': {
                'ru': 'Невозможно выполнить операцию.',
                'uz': 'To`lovni amalga oshirib bo`lmaydi.',
                'en': 'The operation could not be performed.'
            },
        }

    return {
        'result': {
            'state': transaction.state,
            'create_time': int(transaction.created_at.timestamp() * 1000),
            'transaction': transaction.token
        }
    }


def check_transaction(transaction):
    return {
        'result': {
            'state': transaction.state,
            'create_time': int(transaction.created_at.timestamp() * 1000),
            'transaction': transaction.token,
            'perform_time': int(transaction.payed_at.timestamp() * 1000) if transaction.payed_at else 0,
            'cancel_time': int(transaction.canceled_at.timestamp() * 1000) if transaction.canceled_at else 0,
            'reason': transaction.reason,
        }
    }


def perform_transaction(transaction):
    if transaction.state == 1:
        now = datetime.now(transaction.payme_created_at.tzinfo) + timedelta(hours=5)
        transaction_expires_at = transaction.payme_created_at + timedelta(hours=12)
        if transaction_expires_at < now:
            print('transaction expired', now)
            transaction.is_active = False
            transaction.state = -1
            transaction.reason = 4

            return {
                'code': -31008,
                'message': {
                    'ru': 'Невозможно выполнить операцию.',
                    'uz': 'To`lovni amalga oshirib bo`lmaydi.',
                    'en': 'The operation could not be performed.'
                },
            }
        transaction.payed_at = datetime.now()
        transaction.is_payed = True
        transaction.state = 2

        transaction.course.students.add(transaction.student)
        transaction.group.students.add(transaction.student)

        return {
            'result': {
                'state': transaction.state,
                'perform_time': int(transaction.payed_at.timestamp() * 1000),
                'transaction': transaction.token
            }
        }

    if transaction.state == 2:
        return {
            'result': {
                'state': transaction.state,
                'perform_time': int(transaction.payed_at.timestamp() * 1000),
                'transaction': transaction.token
            }
        }

    return {
        'code': -31008,
        'message': {
            'ru': 'Невозможно выполнить операцию.',
            'uz': 'To`lovni amalga oshirib bo`lmaydi.',
            'en': 'The operation could not be performed.'
        },
    }


def cancel_transaction(data, transaction):
    params = data.get('params')

    if transaction.state == 1:
        transaction.state = -1
        transaction.reason = params.get('reason')
        transaction.canceled_at = datetime.now()

        return {
            'result': {
                'state': transaction.state,
                'cancel_time': int(transaction.canceled_at.timestamp() * 1000),
                'transaction': transaction.token
            }
        }

    if transaction.state == 2:
        transaction.group.students.remove(transaction.student)
        transaction.course.students.remove(transaction.student)

        transaction.state = -2
        transaction.reason = params.get('reason')
        transaction.canceled_at = datetime.now()
        transaction.is_payed = False
        transaction.save()

    return {
        'result': {
            'state': transaction.state,
            'cancel_time': int(transaction.canceled_at.timestamp() * 1000),
            'transaction': transaction.token
        }
    }
