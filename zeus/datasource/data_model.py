# -*- coding: utf-8 -*-
from zeus.libs.log import logger


class DataModel(object):
    """
    DataModel is a abstract of data source.
    data source, eg: prometheus
    """

    def query(self, data_source, query):
        logger.info("data_source: {data_source}"
                    .format(data_source=data_source))
        logger.info("query: {query}".format(query=query))


class DataSource(object):
    """
    DataSource defines config for data source
    """

    def __init__(self, url):
        self.url = url





