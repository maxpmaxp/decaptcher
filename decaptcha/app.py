# -*- coding: utf-8 -*-
import logging
from collections import defaultdict

from bottle import Bottle, run, request

from solvers import SolversRegistry

app = Bottle()

log = logging
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.DEBUG)

counters = defaultdict(int)
checkers = {
    'one': lambda: False,
    'two': lambda: True,
}

# single access
def increment_counter(solver_name):
    counters[solver_name] += 1


def is_appropriate(solver_name):
    if counters[solver_name] % 1000 == 0:
        checker = checkers.get(solver_name)
        return checker() if checker else True


@app.route('/', method='POST')
def solve_captcha():
    img = request.POST.get('img')
    if not img:
        error = "No 'img' param in POST data"
        log.error(error)
        return {"error": error}

    registry = SolversRegistry()
    print registry

    solver_name = request.query.get("upstream_service")
    if solver_name:
        solver = registry.get_by_name(solver_name)
    else:
        solver = registry.get()
        if not is_appropriate(solver['name']):
            solver = registry.get_next()

    if solver is None:
        if solver_name:
            solvers_str = ",".join(registry.solvers_names)
            error = ("Not found 'upstream_service' with name %r. "
                     "Available only %s" % (solver_name, solvers_str))
        else:
            error = "Solvers left out"
        log.error(error)
        return {"error": error}

    while True:
        code, error = solver['cb'](img)
        if error:
            log.error("%s, solver %s", error, solver['name'])
            solver = registry.get_next()

    if not error:
        increment_counter(solver['name'])
        log.debug(u"Captcha code %s, solver %s", code, solver['name'])
    return {'code': code, 'error': error}


if __name__ == '__main__':
    run(app, host='localhost', port=8020, reloader=True, debug=True)
