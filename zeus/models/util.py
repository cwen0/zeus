# -*- coding: utf-8 -*-

JOB_ID_LEN = 8


def sub_id(st):
    if len(st) < JOB_ID_LEN:
        return st

    return st[0:JOB_ID_LEN]
