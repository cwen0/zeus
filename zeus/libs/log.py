import os
import logging
from inner_conf import LOG_DIR
import sys


def get_logger():
    '''
    @summary: init logger
    @result: return a logger object
    '''
    logger_ = logging.getLogger("employee_account")
    formatter = logging.Formatter(
        fmt='[%(asctime)s %(filename)s:%(lineno)d] %(message)s',
        datefmt='%y/%m/%d %H:%M:%S')
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger_.addHandler(handler)
    logger_.setLevel(logging.DEBUG)
    return logger_


# if not os.path.isdir(LOG_DIR):
#     os.makedirs(LOG_DIR)
logger = get_logger()
