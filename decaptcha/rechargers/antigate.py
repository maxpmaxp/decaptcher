# -*- coding: utf-8 -*-

from settings import Solvers
from . import base


def round_to_increment(value, increment):
    """
    >>> round_to_increment(74, 50)
    50.0
    >>> round_to_increment(76, 50)
    100.0
    """
    return increment * round(value * 1. / increment, 0)


class AntigateData(base.AvangateData):
    product_id = '4537860'
    product_price = 50
    input_service_login = 'custom[2398]'

    def product_quantity(self, avail_sum):
        return 1


class AntigateRecharger(base.RechargerViaAvangate):
    service_name = Solvers.ANTIGATE
    data_cls = AntigateData

    def auto_run(self):
        amount = self.get_sum_to_recharge()
        price = self.data.product_price
        for _ in range(amount / price):
            self.run(price)

    def get_sum_to_recharge(self):
        """ Return the sum we need to put in account's balance """
        to_recharge = super(AntigateRecharger, self).get_sum_to_recharge()
        return round_to_increment(to_recharge, self.data.product_price)
