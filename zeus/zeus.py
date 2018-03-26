# -*- coding: utf-8 -*-
import tornado.web
import tornado.gen
import uuid
import threading
from libs.log import logger
import json
import models

HTTP_MISS_ARGS = 401
HTTP_FAIL = 403
HTTP_OK = 200

jobs = dict()
lock = threading.Lock()


class ModelHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def run(self, job):
        if job.model not in models.models:
            raise ValueError("model: {model} is not supported"
                             .format(model=job.model))

        model = models.models[job.model]
        runner = model(job)
        with lock:
            jobs[job.id] = runner

        runner.run()


class JobNewHandler(ModelHandler):
    @tornado.web.asynchronous
    def post(self):
        data = json.loads(self.request.body)
        try:
            job = models.Job(str(uuid.uuid4()), data["data_source"],
                data["model"], data["metrics"])
        except KeyError as e:
            self.finish({"code": HTTP_MISS_ARGS,
                         "message": "miss args %s" % e.args[0]})

        try:
            logger.info("run new job:{job}"
                        .format(job=dict(job)))
            self.run(job)
        except Exception as e:
            logger.error("run job:{job} failed"
                         .format(job=dict(job)))
            self.finish({"code": HTTP_FAIL,
                         "message": "run job:{job} failed"
                        .format(job=dict(job))})
        self.finish({"code": HTTP_OK,
                     "message": "OK",
                     "data": json.dump(dict(job))})


# class JobDetailHandler(ModelHandler):
#
# class JobDeleteHandler(ModelHandler):
#
# class JobListHandler(ModelHandler):


def make_app():
    return tornado.web.Application([
        (r"/api/v1/job/new", JobNewHandler),
        # (r"/api/v1/job/detail", JobDetailHandler),
        # (r"/api/v1/job/delete", JobDeleteHandler),
        # (r"/api/v1/jon/list", JobListHandler),
    ])



