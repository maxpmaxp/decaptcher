# -*- coding: utf-8 -*-
import logging
import logging.config
from collections import OrderedDict

from argh import arg, dispatch_command, CommandError

from rechargers import RECHARGERS
from storage.redis import RedisStorage
from settings import CARD_USER, CARD_INFO, CHECK_BALANCE_INTERVAL, LOGGING


logging.config.dictConfig(LOGGING)
log = logging.getLogger('recharger')
ALL_SERVICES = RECHARGERS.keys()


def init_user_dict():
    return OrderedDict([
        ('language', 'en'),
        ('display_currency', 'USD'),
        ('checkout_type', 'person'),
        ('fname', CARD_USER['firstname']),
        ('lname', CARD_USER['lastname']),
        ('address', CARD_USER['address']),
        ('city', CARD_USER['city']),
        ('zipcode', CARD_USER['zipcode']),
        ('billingcountry', '222'),
        ('stateis', 'drop'),
        ('state', CARD_USER['state']),
        ('email', CARD_USER['email']),
        ('re_email', CARD_USER['email']),
        ('samedelivery', 'Yes'),
        ('payment', '1'),
        ('billing_currency', 'USD'),
        ('Submit', 'Continue'),
    ])


def init_card_dict():
    return OrderedDict([
        ('ccnumber', CARD_INFO['number']),
        ('cardtype', '-1'),
        ('ccexpmonth', CARD_INFO['expmonth']),
        ('ccexpyear', CARD_INFO['expyear']),
        ('cvv2', CARD_INFO['cvv2']),
        ('nameoncard', CARD_INFO['nameoncard']),
        ('Authorize', 'Authorize'),
    ])


def get_selected_services(args):
    if args.all:
        return ALL_SERVICES
    elif args.only:
        return args.only
    else:
        raise CommandError("Supply either --all or --only options")


@arg('-a', '--all', action='store_true', help='Run for all solvers')
@arg('-o', '--only', choices=ALL_SERVICES, metavar='x', nargs='*', help=
     'Run for selected only. Allowed values are %s' % ', '.join(ALL_SERVICES))
def main(args):
    """ Recharge solvers balance """
    storage = RedisStorage()
    user = init_user_dict()
    card = init_card_dict()
    services = get_selected_services(args)
    log.debug(u"Selected services: %s", ", ".join(services))

    for service in services:
        recharge_timer = 'recharge:%s' % service
        if storage.timer_expired(recharge_timer):
            log.debug(u"[%s] Timer expired. Run recharger", service)
            recharger = RECHARGERS[service](user, card)
            recharger.auto_run()
            storage.start_timer(recharge_timer, seconds=CHECK_BALANCE_INTERVAL)


if __name__ == '__main__':
    dispatch_command(main)
