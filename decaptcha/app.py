# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import logging.config

from bottle import Bottle, run, request

import settings
import solvers.api as solvers
from solvers.de_captcher import ResultCodes
from storage.redis import RedisStorage
from checkers import check_solver
from errors import SolverError


app = Bottle()

logging.config.dictConfig(settings.LOGGING)
log = logging.getLogger('app')


def validate_user(username, password):
    correct_username = (username == settings.APP_ACCESS['username'])
    correct_password = (password == settings.APP_ACCESS['password'])
    return correct_username and correct_password


def check_request(request):
    data = request.POST
    query = request.query
    try:
        user = (data['username'], data['password'])
    except KeyError:
        return u"Нет параметров 'username', 'password' в POST-данных"

    if not validate_user(*user):
        return u"Неверный логин/пароль (%s/%s)" % user
    elif 'pict' not in data:
        return u"Нет параметра 'pict' в POST-данных"
    elif query:
        service_name = query.get("upstream_service")
        if not service_name:
            return u"%s вместо 'upstream_service' в запросе" %  query.keys()
        elif service_name not in settings.Solvers.names:
            return u"Неизвестный upstream_service %s" % service_name
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

    while True:
        try:
            storage.incr_uses(solver['name'])
            code = solver['cb'](pict)
            break
        except SolverError as error:
            storage.incr_fails(solver['name'])
            log.error(u"[%s] Ошибка: %s", solver['name'], error.message)
            solver = solvers.get_next(solver['name'])

    log.debug(u"[%s] Код капчи %s", solver['name'], code)
    return decaptcher_response(captcha_code=code)


@app.route('/ban/<solver>')
def ban(solver):
    """
    Перманентная блокировка сервиса-расшифровшика 'solver'
    """
    storage = RedisStorage()
    storage.ban(solver)


@app.route('/unban/<solver>')
def unban(solver):
    """
    Разблокировка сервиса-расшифровшика 'solver'
    """
    storage = RedisStorage()
    storage.unban(solver)


if __name__ == '__main__':
    run(app, host='localhost', port=8020, reloader=True, debug=True)
