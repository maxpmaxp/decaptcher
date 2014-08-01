# -*- coding: utf-8 -*-

from settings import Solvers
from . import base


class DeathbycaptchaData(base.AvangateDataTwo):
    product_id = '4533249'
    product_price = 6.95

    def product(self, avail_sum):
        """ avail_sum - sum to put in account's balance """
        d = super(DeathbycaptchaData, self).product(avail_sum)
        d.update([
            ('CART', '2'),
            ('REF', self.service_login),
        ])
        return d


class DeathbycaptchaRecharger(base.RechargerViaAvangate):
    service_name = Solvers.DEATH_BY_CAPTCHA
    data_cls = DeathbycaptchaData
