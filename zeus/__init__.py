# -*- coding: utf-8 -*-
from .datasource import (
    DataSource,
    DataModel,
)

from .models import (
    IForest,
    Model,
    Job,
    models,
)

from .app import (
    parse_config,
)

from .zeus import (
    make_app,
)

from .libs.log import logger

from tornado.options import options
import tornado.ioloop


def main():
    parse_config()

    app = make_app()
    logger.info("zeus server start to listen {port}..."
                .format(port=options.port))
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
