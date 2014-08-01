# -*- coding: utf-8 -*-

from settings import Solvers
from . import base


class CaptchabotData(base.AvangateDataTwo):
    product_id = '4568174'
    product_price = 10

    def product(self, avail_sum):
        """ avail_sum - sum to put in account's balance """
        d = super(CaptchabotData, self).product(avail_sum)
        d.update([
            ('CART', '1'),
            ('CARD', '1'),
            ('REF', '37184'),
            ('LANG', 'en'),
            ('ORDERSTYLE', 'nLW84pa5rn4%3D'),
        ])
        return d


class CaptchabotRecharger(base.RechargerViaAvangate):
    service_name = Solvers.CAPTCHABOT
    data_cls = CaptchabotData
