# -*- coding: utf-8 -*-

from datasource import PrometheusAPI, PrometheusQuery, Metrics
from sklearn.ensemble import IsolationForest
from threading import Event
import time
import numpy as np
import pandas as pd
import datetime
import random
from model import Model
from util import sub_id
from libs.log import logger


class IForest(Model):
    def __init__(self, job, callback):
        self.job = job
        self.callback = callback
        self.api = PrometheusAPI(job.data_source)
        self.df = pd.DataFrame(columns=["mean", "std"])
        self.ilf = IsolationForest(n_estimators=100,
                                   n_jobs=-1, verbose=2)
        self.event = Event()
        # TODO: make them configurable.
        self.train_count = 120
        self.train_interval = 60
        self.predict_interval = 120
        self.__exit = False

    def train(self, query_expr):
        logger.info("[job-id:{id}] starting to get sample data"
                    .format(id=sub_id(self.job.id)))
        for index in range(0, self.train_count, 1):
            if self.__exit:
                logger.info("[job-id:{id}] stop job"
                            .format(id=sub_id(self.job.id)))
                return False

            now = datetime.datetime.now()
            query = PrometheusQuery(query_expr,
                                    time.mktime((now - datetime.timedelta(minutes=15)).timetuple()),
                                    time.mktime(now.timetuple()), "15s")
            self.train_task(query)

            if index % 10 == 0:
                mean_value = float(random.randint(0, 5000))
                std_value = float(random.randint(0, 10000))
                df_one = {"mean": mean_value, "std": std_value}
                self.df = self.df.append(df_one, ignore_index=True)

                logger.info("[job-id:{id}] append data to train df:{df_one}"
                            .format(id=sub_id(self.job.id), df_one=df_one))

            self.event.wait(self.train_interval)
        x_cols = ["mean", "std"]
        logger.info("[job-id:{id}] starting to train sample data"
                    .format(id=sub_id(self.job.id)))
        self.ilf.fit(self.df[x_cols])
        return True

    def train_task(self, query):
        data_set = self.api.query(query)
        if len(data_set) > 0:
            values = []
            for data in data_set.values():
                values.append(float(data))

            mean_value = np.mean(values)
            std_value = np.std(values)
            df_one = {"mean": mean_value, "std": std_value}

            logger.info("[job-id:{id}] append data to train df:{df_one}"
                        .format(id=sub_id(self.job.id), df_one=df_one))
            self.df = self.df.append(df_one, ignore_index=True)

    def predict(self, query_expr):
        logger.info("[job-id:{id}] starting to predict"
                    .format(id=sub_id(self.job.id)))
        while not self.__exit:
            now = datetime.datetime.now()
            query = PrometheusQuery(query_expr,
                                    time.mktime((now - datetime.timedelta(minutes=5)).timetuple()),
                                    time.mktime(now.timetuple()), "15s")

            if self.predict_task(query) == 1:
                logger.info("[job-id:{id}] predict OK"
                            .format(id=sub_id(self.job.id)))
            else:
                logger.info("[job-id:{id}] Predict Error"
                            .format(id=sub_id(self.job.id)))
                self.callback("[job-id] {id}, predict metrics error in last {time}s"
                              .format(id=sub_id(self.job.id),
                                      time=self.predict_interval),
                              job.slack_channel)

            self.event.wait(self.predict_interval)
        logger.info("[job-id:{id}] stop job"
                    .format(id=sub_id(self.job.id)))

    def predict_task(self, query):
        data_set = self.api.query(query)
        values = []
        for data in data_set.values():
            values.append(float(data))

        mean_value = np.mean(values)
        std_value = np.std(values)
        predict_data = np.array([[mean_value, std_value]])

        logger.info("[job-id:{id}] predict data:{predict_data}"
                    .format(id=sub_id(self.job.id), predict_data=predict_data))
        return self.ilf.predict(predict_data)

    def run(self):
        for key in self.job.metrics:
            if key in Metrics:
                val = Metrics[key]
                if self.train(val):
                    self.predict(val)

    def close(self):
        # TODO: close this job
        logger.info("[job-id:{id}] closing the job"
                    .format(id=sub_id(self.job.id)))
        self.__exit = True
        self.event.set()



