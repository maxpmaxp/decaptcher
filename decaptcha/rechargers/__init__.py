# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .antigate import AntigateRecharger
from .captchabot import CaptchabotRecharger
from .deathbycaptcha import DeathbycaptchaRecharger
from .de_captcher import DecaptcherRecharger


RECHARGERS = {
    r.service_name: r for r in
    [AntigateRecharger, CaptchabotRecharger,
     DeathbycaptchaRecharger, DecaptcherRecharger]
}
