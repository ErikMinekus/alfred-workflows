# encoding: utf-8

import eiscp


def discoverReceiver():
    return next(iter(eiscp.eISCP.discover(timeout=1)), None)
