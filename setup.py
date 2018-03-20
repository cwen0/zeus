from prometheus import PrometheusAPI
from prometheus import Query
from sklearn.ensemble import IsolationForest
from libs.log import logger
import time
import numpy as np
import pandas as pd
import argparse
import datetime
import sys
import random

QUERY_QPS_EXPR = "sum(rate(tidb_server_query_total[1m])) by (status)"


class ZeusIsolationForest(object):
    def __init__(self, query_expr, data_url, train_count=60, train_interval=60, predict_interval=60):
        self.query_expr = query_expr
        self.data_url = data_url
        self.train_count = train_count
        self.train_interval = train_interval
        self.predict_interval = predict_interval
        self.api = PrometheusAPI()
        self.df = pd.DataFrame(columns=["mean", "std"])
        self.ilf = IsolationForest(n_estimators=100,
                                   n_jobs=-1, verbose=2)

    def train(self):
        logger.info("starting to get sample data")
        for index in range(0, self.train_count, 1):
            now = datetime.datetime.now()
            query = Query(self.query_expr,
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
        data_set = self.api.range_query(self.data_url, query)
        if len(data_set) > 0:
            values = []
            for data in data_set.values():
                values.append(float(data))

            mean_value = np.mean(values)
            std_value = np.std(values)
            df_one = {"mean": mean_value, "std": std_value}

            logger.info("append data to train df:{df_one}".format(df_one=df_one))
            self.df = self.df.append(df_one, ignore_index=True)

    def predict(self):
        logger.info("starting to predict")
        while True:
            now = datetime.datetime.now()
            query = Query(self.query_expr,
                          time.mktime((now - datetime.timedelta(minutes=5)).timetuple()),
                          time.mktime(now.timetuple()), "15s")
            if self.predict_task(query) == 1:
                print("test OK")
            else:
                print("test Error")

            time.sleep(self.predict_interval)

    def predict_task(self, query):
        data_set = self.api.range_query(self.data_url, query)
        values = []
        for data in data_set.values():
            values.append(float(data))

        mean_value = np.mean(values)
        std_value = np.std(values)
        predict_data = np.array([[mean_value, std_value]])

        logger.info("predict data:{predict_data}".format(predict_data=predict_data))
        return self.ilf.predict(predict_data)


def parse_args():
    parser = argparse.ArgumentParser(description="metric warning")

    parser.add_argument("--url", action="store_true", dest="data_url",
                        default="http://40.125.162.12:36722", required=False)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    kwargs = vars(args)
    if kwargs["data_url"] == "":
        print "Error: url is necessary"
        sys.exit(1)

    ilf = ZeusIsolationForest(QUERY_QPS_EXPR, kwargs["data_url"])
    ilf.train()
    ilf.predict()


if __name__ == "__main__":
    main()
