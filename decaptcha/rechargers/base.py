# -*- coding: utf-8 -*-
import re
import time
import math
import logging
from collections import OrderedDict
from functools import partial
from os.path import dirname, join

import requests
from pyquery import PyQuery
from retry import retry

import settings
from utils import mkdir_p, union_dicts
from errors import CaptchaFound
from solvers.api_list import get_api


log = logging.getLogger('recharger')

URL_ORDER = "https://secure.avangate.com/order/"
URLS = {
    'checkout': URL_ORDER + "checkout.php",
    'place_order': URL_ORDER + "ccprocess.php",
    'result': URL_ORDER + "finish.php",
}


def write(data, filepath):
    with open(filepath, 'wb') as f:
        f.write(data)


def save_html(data, filename, key):
    path = join(settings.LOG_DIR, key, filename + '.html')
    try:
        write(data, path)
    except IOError:
        mkdir_p(dirname(path))
        write(data, path)


def find_cart_id(page_html):
    return re.search(r"CART_ID=(\w+)", page_html, re.I).group(1)


def find_elem(page_html, element_selector):
    return PyQuery(page_html)(element_selector)


def wait_until_element(browser, url, element_selector, timeout=20):
    assert timeout > 0
    timeout = int(math.ceil(timeout))

    step = 1
    for attempt in range(0, timeout, step):
        resp = browser(url)
        if find_elem(resp.content, element_selector):
            break
        time.sleep(step)
    return resp


class AvangateData(object):
    """
    Data for default 3-step payment:
    - product info
    - billing info
    - credit card info & placing order
    """
    product_id = None
    product_price = None
    input_service_login = None

    def __init__(self, service_name, user, card):
        self.service_login = settings.ACCOUNTS[service_name]['username']
        self.card = card.copy()
        self.bill = user.copy()
        if self.input_service_login:
            self.bill[self.input_service_login] = self.service_login

    def product_quantity(self, avail_sum):
        return math.floor(avail_sum / self.product_price)

    def product(self, avail_sum):
        """ avail_sum - sum to put in account's balance """
        return OrderedDict([
            ('CURRENCY', 'USD'),
            ('PRODS', self.product_id),
            ('QTY', self.product_quantity(avail_sum)),
        ])

    def checkout_start(self):
        return self.bill

    def checkout_fin(self, current_page):
        return self.card


class AvangateDataTwo(AvangateData):
    """
    Data for 2-step payment:
    - product info
    - billing and credit card info
    - placing order
    """
    def checkout_start(self):
        return union_dicts(self.bill, self.card)

    def checkout_fin(self, page_html):
        token_name = '_avg8_tk'
        token = find_elem(page_html, 'input[name=%s]' % token_name).val()
        return OrderedDict([
            (token_name, token),
            ('Authorize', 'Authorize'),
        ])


class RechargerViaAvangate(object):
    balance_checker = None
    data_cls = None
    service_name = None

    def __init__(self, user, card):
        self.data = self.data_cls(self.service_name, user, card)
        if not self.balance_checker:
            self.balance_checker = get_api(self.service_name).balance

    def auto_run(self):
        self.run(self.get_sum_to_recharge())

    @retry(CaptchaFound, tries=1, delay=600)
    def run(self, amount):
        """ Put the 'amount' of money in account's balance """
        if not amount:
            return
        s = self.session = requests.Session()
        data = self.data

        # send product's quantity
        resp = s.get(URLS['checkout'], params=data.product(amount))
        self.save(resp, '1')

        cart_id = find_cart_id(resp.content)
        _post = partial(s.post, params={"CART_ID": cart_id})
        _get = partial(s.get, params={"CART_ID": cart_id})

        # send person details, next - card page
        resp = _post(URLS['checkout'], data=data.checkout_start())
        self.save(resp, '2')
        if find_elem(resp.content, 'img#img_capcha'):
            raise CaptchaFound('Captcha found')

        # send card details, next - page with js code,
        # so need to load result (finish) page manually
        resp = _post(URLS['place_order'], data=data.checkout_fin(resp.content))
        self.save(resp, '3')

        # some services needs additional step to authorize payment
        self.verify_payment(resp)

        # load result page for logging purpose
        # wait until order processing will be finished
        resp = wait_until_element(_get, URLS['result'], 'div#order__page__finish')
        self.save(resp, 'result')

    def verify_payment(self, resp):
        pass

    def get_sum_to_recharge(self):
        """ Return the sum we need to put into balance """
        balance = self.balance_checker()
        if balance > settings.MIN_BALANCE:
            self.log(u"Current balance %s - no need to refill", balance)
            return 0
        to_recharge = 250 - balance
        # recharge at least MIN_RECHARGE_AMOUNT,
        # but no more than MAX_RECHARGE_AMOUNT
        to_recharge = max(settings.MIN_RECHARGE_AMOUNT, to_recharge)
        to_recharge = min(settings.MAX_RECHARGE_AMOUNT, to_recharge)
        self.log(u"Current balance %s - refill for %s", balance, to_recharge)
        return to_recharge

    def save(self, resp, filename):
        if settings.DEBUG:
            save_html(resp.content, filename, key=self.service_name)

    def log(self, msg, *args):
        log.debug(u"[%s] %s", self.service_name, msg % args)
