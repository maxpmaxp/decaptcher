# -*- coding: utf-8 -*-

import requests

from settings import Solvers
from . import base


def auto_post_form(page_html, form_name):
    form = base.find_elem(page_html, 'form[name=%s]' % form_name)
    form_url = form.attr('action')
    form_data = {i.name: i.value for i in form('input')}
    return requests.post(form_url, data=form_data)


class DecaptcherData(base.AvangateData):
    product_id = '4515131'
    product_price = 10
    input_service_login = 'custom_4515131[1951]'


class DecaptcherRecharger(base.RechargerViaAvangate):
    service_name = Solvers.DE_CAPTCHER
    data_cls = DecaptcherData

    def verify_payment(self, resp):
        resp = auto_post_form(resp.content, 'downloadForm')
        self.save(resp, 'verify1')
        resp = auto_post_form(resp.content, 'downloadForm')
        self.save(resp, 'verify2')
