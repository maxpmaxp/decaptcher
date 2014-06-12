# -*- coding: utf-8 -*-

import errors
import settings
from settings import Solvers, CheckErrors
from solvers.api_list import SOLVER_APIS
from solvers.api import LOWEST_SOLVER

#TODO: удалить функции, связанные с балансом,
# если также не будут использоваться

def is_service_expensive(service_name, storage):
    api = SOLVER_APIS[service_name]
    recent_balance = storage.get_balance(service_name)
    current_balance = api.balance()
    max_delta = settings.get_max_cost(service_name)
    return recent_balance - current_balance > max_delta


def update_balance(service_name, storage):
    current_balance = SOLVER_APIS[service_name].balance()
    storage.set_balance(service_name, current_balance)


# storage.get_counter нет, добавить если вдруг понадобится эта функция.

# def is_service_ok(service_name, storage):
#     """
#     Проверяем удовлетворяет ли нас сервис 'service_name'
#     по стоимости расшифровки 1000 капч.
#     """
#     counter = storage.get_counter(service_name)
#     if not counter:
#         update_balance(service_name, storage)
#         return True
#     elif counter % 1000 == 0:
#         update_balance(service_name, storage)
#         return not is_service_expensive(service_name, storage)
#     else:
#         return True


def is_fails_percentage_ok(service_name, storage):
    """
    Проверка процента ошибок при использовании сервиса 'service_name'
    """
    uses_num = storage.get_uses(service_name)
    if not uses_num:
        return True
    fails_num = storage.get_fails(service_name)
    fails_percentage = float(fails_num) / uses_num * 100
    return fails_percentage <= settings.MAX_FAILS_PERCENTAGE


def is_antigate_minbid_ok():
    """
    Проверка значения минимальной ставки
    за расшифровку капчи на antigate.com
    """
    api = SOLVER_APIS[Solvers.ANTIGATE]
    try:
        minbid = api.minbid()
    except errors.SolverError:
        #TODO: log error
        return True
    else:
        return minbid * 1000 <= settings.ANTIGATE_MAX_PRICE


def check_solver(service_name, storage):
    if service_name == LOWEST_SOLVER:
        return None

    no_uses = not storage.get_uses(service_name)
    if service_name == Solvers.ANTIGATE\
            and (no_uses or storage.timer_expired("minbid"))\
            and not is_antigate_minbid_ok():
        return CheckErrors.MINBID

    if storage.timer_expired("fails")\
            and not is_fails_percentage_ok(service_name, storage):
        return CheckErrors.FAILS
    return None
