# -*- coding: utf-8 -*-
from zeus.libs.log import logger


class Model(object):
    """Model is a abstract of calculation model."""

    def run(self):
        logger.info("running calculation model")
