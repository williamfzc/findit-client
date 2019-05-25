import logzero
import logging


def switch_log(status):
    if status:
        logzero.loglevel(logging.INFO)
    else:
        logzero.loglevel(logging.ERROR)


# default: no log
switch_log(False)
