# -*- coding: utf-8 -*-

from zeus.datasource import PrometheusAPI, PrometheusQuery, Metrics
from sklearn.ensemble import IsolationForest
from zeus.libs.log import logger
import time
import numpy as np
import pandas as pd
import datetime
import random
from model import Model


class IForest(Model):
    # def __init__(self, query_expr, data_url, train_count=60, train_interval=60, predict_interval=60):
    #     self.query_expr = query_expr
    #     self.data_url = data_url
    #     self.train_count = train_count
    #     self.train_interval = train_interval
    #     self.predict_interval = predict_interval
    #     self.api = PrometheusAPI()
    #     self.df = pd.DataFrame(columns=["mean", "std"])
    #     self.ilf = IsolationForest(n_estimators=100,
    #                                n_jobs=-1, verbose=2)
    def __init__(self, job):
        self.job = job
        self.api = PrometheusAPI(job.data_source)
        self.df = pd.DataFrame(columns=["mean", "std"])
        self.ilf = IsolationForest(n_estimators=100,
                                   n_jobs=-1, verbose=2)
        # TODO: make them configurable.
        self.train_count = 120
        self.train_interval = 60
        self.predict_interval = 120

    def train(self, query_expr):
        logger.info("starting to get sample data")
        for index in range(0, self.train_count, 1):
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

                logger.info("append data to train df:{df_one}".format(df_one=df_one))

            time.sleep(self.train_interval)
        x_cols = ["mean", "std"]
        logger.info("starting to train sample data")
        self.ilf.fit(self.df[x_cols])

    def train_task(self, query):
        data_set = self.api.query(query)
        if len(data_set) > 0:
            values = []
            for data in data_set.values():
                values.append(float(data))

            mean_value = np.mean(values)
            std_value = np.std(values)
            df_one = {"mean": mean_value, "std": std_value}

            logger.info("append data to train df:{df_one}".format(df_one=df_one))
            self.df = self.df.append(df_one, ignore_index=True)

    def predict(self, query_expr):
        logger.info("starting to predict")
        while True:
            now = datetime.datetime.now()
            query = PrometheusQuery(query_expr,
                                    time.mktime((now - datetime.timedelta(minutes=5)).timetuple()),
                                    time.mktime(now.timetuple()), "15s")
            if self.predict_task(query) == 1:
                logger.info("test OK")
            else:
                logger.info("test Error")

            time.sleep(self.predict_interval)

    def predict_task(self, query):
        data_set = self.api.query(query)
        values = []
        for data in data_set.values():
            values.append(float(data))

        mean_value = np.mean(values)
        std_value = np.std(values)
        predict_data = np.array([[mean_value, std_value]])

        logger.info("predict data:{predict_data}".format(predict_data=predict_data))
        return self.ilf.predict(predict_data)

    def run(self):
        for key in self.job.metrics:
            if key in Metrics:
                val = Metrics[key]
                self.train(val)
                self.predict(val)

    def close(self):
        # TODO: close this job
        logger.info("closing the job")


