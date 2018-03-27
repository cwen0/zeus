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

runners = dict()
lock = threading.Lock()


class ModelHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=24)

    @tornado.gen.coroutine
    def run(self, job):
        if job.model not in models.models:
            raise ValueError("model:{model} is not supported"
                             .format(model=job.model))
            # raise ModelNotSupportException(model_name=job.model)

        model = models.models[job.model]
        runner = model(job, alert.send_to_slack)
        lock.acquire()
        runners[job.id] = runner
        lock.release()

        result = yield self._async_execute(runner)
        raise tornado.gen.Return(result)

    @tornado.concurrent.run_on_executor
    def _async_execute(self, runner):
        runner.run()
        return True

    def close_job(self, job_id):
        if job_id not in runners:
            raise ValueError("job:{job_id} is not running"
                             .format(job_id=job_id))
            # raise JobNotExistsException(job_id=job_id)
        lock.acquire()
        runner = runners[job_id]
        runner.close()

        del runners[job_id]
        lock.release()

    def list_jobs(self):
        lock.acquire()
        jobs = []
        for job_id, runner in runners.items():
            job = dict(runner.job)
            jobs.append(job)
        lock.release()
        return jobs

    def detail_job(self, job_id):
        if job_id not in runners:
            raise ValueError("job:{job_id} is not running"
                             .format(job_id=job_id))
            # raise JobNotExistsException(job_id=job_id)
        lock.acquire()
        runner = runners[job_id]
        lock.release()

        return dict(runner.job)


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
            self.finish({"code": HTTP_OK,
                        "message": "OK",
                         "data": dict(job)})
        except Exception as e:
            logger.error("run job:{job} failed:{err}"
                         .format(job=dict(job), err=e))
            self.finish({"code": HTTP_FAIL,
                         "message": "run job:{job} failed:{err}"
                        .format(job=dict(job), err=e)})


class JobDeleteHandler(ModelHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, job_id):
        if job_id == "":
            logger.error("job id is required")
            self.finish({"code": HTTP_MISS_ARGS,
                         "message": "job id is required"})

        try:
            logger.info("close running job:{job_id}"
                        .format(job_id=job_id))
            self.close_job(job_id)
            self.finish({"code": HTTP_OK,
                        "message": "OK"})
        except Exception as e:
            logger.error("close job:{job_id} failed:{err}"
                         .format(job_id=job_id, err=e))
            self.finish({"code": HTTP_FAIL,
                         "message": "close job:{job_id} failed:{err}"
                        .format(job_id=job_id, err=e)})


class JobListHandler(ModelHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        logger.info("list all running jobs")
        jobs = self.list_jobs()
        logger.info("running jobs:{jobs}"
                    .format(jobs=jobs))
        self.finish({"code": HTTP_OK,
                    "message": "OK",
                     "data": jobs})


class JobDetailHandler(ModelHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, job_id):
        if job_id == "":
            logger.error("job id is required")
            self.finish({"code": HTTP_MISS_ARGS,
                         "message": "job id is required"})

        try:
            logger.info("get job:{job_id} detail"
                        .format(job_id=job_id))
            job = self.detail_job(job_id)
            self.finish({"code": HTTP_OK,
                         "message": "OK",
                         "data": job})
        except Exception as e:
            logger.error("get job:{job_id} detail failed:{err}"
                         .format(job_id=job_id, err=e))
            self.finish({"code": HTTP_FAIL,
                         "message": "get job:{job_id} detail failed:{err}"
                        .format(job_id=job_id, err=e)})






