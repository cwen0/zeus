# -*- coding: utf-8 -*-
from libs.log import logger
from datasource.data_model import DataSource
# import json


class Model(object):
    """Model is a abstract of calculation model."""

    def run(self):
        logger.info("running calculation model")

    def close(self):
        logger.info("close model")


class Job(object):
    """Job defines config for calculation job."""
    def __init__(self, id, data_source,
                 model, metrics, slack_channel):
        self.id = id
        self.data_source = DataSource(data_source["url"])
        self.model = model
        self.metrics = metrics
        self.slack_channel = slack_channel
    # def __init__(self, data):
    #     self.__dict__ = json.loads(data)

    def __iter__(self):
        yield "id", self.id
        yield "data_source", dict(self.data_source)
        yield "model", self.model
        yield "metrics", self.metrics
        yield "slack_channel", self.slack_channel
        # return self.__dict__
