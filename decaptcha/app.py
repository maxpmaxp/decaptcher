# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import logging.config

from bottle import Bottle, run, request, abort, auth_basic

import settings
import solvers.api as solvers
from solvers.de_captcher import ResultCodes
from storage.redis import RedisStorage
from checkers import check_solver
from errors import SolverError


app = Bottle()

logging.config.dictConfig(settings.LOGGING)
log = logging.getLogger('app')


def check_user(username, password):
    user = settings.APP_ACCESS
    return username == user['username'] and password == user['password']

# не используется
requires_auth = auth_basic(check_user)


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
    if 'pict' not in data:
        return u"Нет параметра 'pict' в POST-данных"
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


def start_expired_timers(storage):
    storage.start_expired_timer("fails", settings.FAILS_CHECK_INTERVAL)
    storage.start_expired_timer("minbid", settings.MINBID_CHECK_INTERVAL)


# TODO: передавать pict в нужном для API формате.
# TODO: добавить проверку значения 'pict',
# но сперва нужно определиться с тем, что мы ожидаем:
#     или file-like объект
#         в этом случае можно прочитывать его
#         и передавать дальше в виде бинарника.
#     или бинарная строка
@app.route('/', method='POST')
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

    pict = request.POST['pict']
    pict_type = request.POST.get('pict_type')
    storage = RedisStorage()
    start_expired_timers(storage)

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
            log.error(u"[%s] Ошибка: %s", solver['name'], error.message)
            solver = solvers.get_next(solver['name'])
    else:
        return decaptcher_response(result_code=ResultCodes.GENERAL)

    log.debug(u"[%s] Код капчи %s", solver['name'], code)
    return decaptcher_response(captcha_code=code)


if __name__ == '__main__':
    run(app, host='localhost', port=8020, reloader=True, debug=True)
