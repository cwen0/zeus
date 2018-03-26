# -*- coding: utf-8 -*-
from zeus.libs.log import logger


class Model(object):
    """Model is a abstract of calculation model."""

    def run(self):
        logger.info("running calculation model")

    def close(self):
        logger.info("close model")


class Job(object):
   """Job defines config for calculation job."""
   def __init__(self, id, data_source, model, metrics):
       self.id = id
       self.data_source = data_source
       self.model = model
       self.metrics = metrics

   def __iter__(self):
       yield "id", self.id
       yield "data_source", self.data_source
       yield "model", self.model
       yield "metrics", self.metrics
