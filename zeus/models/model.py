# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from zeus.libs.log import logger
from zeus.datasource.data_model import DataSource
# import json


class Model(object):
    """Model is a abstract of calculation model."""

    def run(self):
        logger.info("running calculation model")

    def close(self):
        logger.info("close model")


