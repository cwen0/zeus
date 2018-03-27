# -*- coding: utf-8 -*-
import tornado.gen
import tornado.web
import uuid
import threading
from libs import alert
from libs.log import logger
import json
import models
from concurrent.futures import ThreadPoolExecutor

HTTP_MISS_ARGS = 401
HTTP_FAIL = 403
HTTP_OK = 200

jobs = dict()
lock = threading.Lock()


class ModelHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=24)

    @tornado.gen.coroutine
    def run(self, job):
        if job.model not in models.models:
            raise ValueError("model: {model} is not supported"
                             .format(model=job.model))

        model = models.models[job.model]
        runner = model(job, alert.send_to_slack)
        with lock:
            jobs[job.id] = runner

        result = yield self._async_execute(runner)
        raise tornado.gen.Return(result)

    @tornado.concurrent.run_on_executor
    def _async_execute(self, runner):
        runner.run()
        return True


class JobNewHandler(ModelHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        data = json.loads(self.request.body)
        print(data)
        try:
            slack_channel = alert.DEFAULT_CHANNEL
            if "slack_channel" in data:
                slack_channel = data["slack_channel"]

            job = models.Job(str(uuid.uuid4()), data["data_source"],
               data["model"], data["metrics"], slack_channel)
            # job = models.Job(data)
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
                     "data": dict(job)})


# class JobDetailHandler(ModelHandler):
#
# class JobDeleteHandler(ModelHandler):
#
# class JobListHandler(ModelHandler):




