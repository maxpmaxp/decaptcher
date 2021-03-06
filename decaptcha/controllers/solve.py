# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging

from bottle import request, abort

import settings
import solvers.api as solvers
from solvers.de_captcher import ResultCodes
from storage.redis import RedisStorage
from checkers import check_solver
from errors import SolverError
from .auth import check_user


log = logging.getLogger('app')


def check_solver_name(name):
    if name not in settings.Solvers.names:
        abort(400, u"Неизвестный upstream_service: %r" % name)
    return None


def check_request(request):
    data = request.POST
    try:
        user = (data['username'], data['password'])
    except KeyError:
        return u"Нет параметров 'username', 'password' в POST-данных"
    if not check_user(*user):
        return u"Неверный логин/пароль (%s/%s)" % user

    query = request.query
    if 'pict' not in request.files:
        return u"'pict' должен быть file-upload"
    elif query:
        service_name = query.get("upstream_service")
        if not service_name:
            return u"%r вместо 'upstream_service' в запросе" %  query.keys()
        else:
            return check_solver_name(service_name)
    else:
        return None


def decaptcher_response(captcha_code=None, result_code=None):
    """ Ответ в формате 'ResultCode|MajorID|MinorID|Type|Timeout|Text' """
    if captcha_code:
        result_code = ResultCodes.OK
    elif result_code:
        captcha_code = 0
    else:
        raise TypeError("No captcha_code or result_code given")
    return "{result_code}|0|0|0|0|{captcha_code}".format(**locals())


def solve_captcha():
    """
    В POST данных нас интересуют username, password, pict.
    Остальные параметры из формата de-captcher не важны.
    Если нас не устроит название или значение
    хотя бы одного параметра, то отдаем ошибку.
    """
    error = check_request(request)
    if isinstance(error, basestring):
        log.error(error)
        return decaptcher_response(result_code=ResultCodes.BAD_PARAMS)

    pict = request.files['pict'].file.read()
    pict_type = request.POST.get('pict_type')
    storage = RedisStorage()

    solver_name = request.query.get("upstream_service")
    if solver_name:
        # TODO: устанавливать ли его текущим или только на один раз
        solver = solvers.get_by_name(solver_name)
    else:
        while True:
            solver = solvers.get_highest_notblocked(storage)
            error_code = check_solver(solver['name'], storage)
            if not error_code:
                break
            block_period = settings.BLOCK_PERIODS[error_code]
            storage.block(solver['name'], block_period)

    for _ in range(settings.MAX_ATTEMPTS_TO_SOLVE):
        try:
            storage.incr_uses(solver['name'])
            code = solver['cb'](pict, pict_type=pict_type)
            break
        except SolverError as error:
            storage.incr_fails(solver['name'])
            log.error(u"[%s] Ошибка: %s", solver['name'], error)
            solver = solvers.get_next(solver['name'])
    else:
        return decaptcher_response(result_code=ResultCodes.GENERAL)

    log.debug(u"[%s] Код капчи %s", solver['name'], code)
    return decaptcher_response(captcha_code=code)
