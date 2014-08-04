# -*- coding: utf-8 -*-

import argh

from storage.redis import RedisStorage


def reset_counters():
    """ Reset counters of fails and uses in storage """
    storage = RedisStorage()
    storage.reset_counters()


if __name__ == '__main__':
    parser = argh.ArghParser()
    parser.add_commands([reset_counters])
    parser.dispatch()
