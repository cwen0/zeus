# -*- coding: utf-8 -*-

from tornado.options import define, options
from .libs.log import logger


define("config", default="", help="path to config file")
define("port", default=2333, multiple=True,
       help="service port")


def parse_config():
    options.parse_command_line()
    if options.config != "":
        logger.info("parse config from config file: {config}"
                    .format(config=options.config) )
        options.parse_config_file(options.config)
    options.parse_command_line()
    logger.info("config: {config}".format(config=options.items()))



