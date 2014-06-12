# -*- coding: utf-8 -*-
"""
Доступ к API сервису-расшифровщика по его названию.
"""
from __future__ import absolute_import

from settings import Solvers
from .de_captcher import DecaptcherAPI
from .captchabot import CaptchabotAPI
from .antigate import AntigateAPI
from .deathbycaptcha import DeathbycaptchaAPI


SOLVER_APIS = {
    Solvers.ANTIGATE: AntigateAPI(),
    Solvers.CAPTCHABOT: CaptchabotAPI(),
    Solvers.DE_CAPTCHER: DecaptcherAPI(),
    Solvers.DEATH_BY_CAPTCHA: DeathbycaptchaAPI(),
}
def get_api(solver_name):
    return SOLVER_APIS[solver_name]
