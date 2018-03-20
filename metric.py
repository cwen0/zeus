from prometheus import PrometheusAPI
from prometheus import Query
from sklearn.ensemble import IsolationForest
import logging
import time
import numpy as np
import pandas as pd
import argparse
import sys

QUERY_QPS_EXPR = "sum(rate(tidb_server_query_total[1m])) by (status)"


class ZeusIsolationForest(object):
    def __init__(self, query_expr, data_url, train_count=60, train_interval=60, predict_interval=60):
        self.query_expr = query_expr
        self.data_url = data_url
        self.train_count = train_count
        self.train_interval = train_interval
        self.predict_interval = predict_interval
        self.api = PrometheusAPI()
        self.df = pd.DataFrame({"mean": [], "std": []})
        self.ilf = IsolationForest(n_estimators=100,
                                   n_jobs=-1, verbose=2)

    def train(self):
        for index in range(0, self.train_count, 1):
            now = time.asctime(time.localtime(time.time()))
            query = Query(self.query_expr, now - 600, now, "15s")
            self.train_task(query)
            time.sleep(self.train_interval)
        x_cols = ["mean", "std"]
        self.ilf.fit(self.df[x_cols])

    def train_task(self, query):
        data_set = self.api.range_query(self.data_url, query)
        self.df.append({"mean": np.mean(data_set.values()),
                        "std": np.std(data_set.values())}, ignore_index=True)

    def predict(self):
        while True:
            now = time.asctime(time.localtime(time.time()))
            query = Query(self.query_expr, now - 600, now, "15s")
            if self.predict_task(query) == 1:
                print("test OK")
            else:
                print("test Error")

            time.sleep(self.predict_interval)

    def predict_task(self, query):
        data_set = self.api.range_query(self.data_url, query)
        return self.ilf.predict({"mean": np.mean(data_set.values()),
                                 "std": np.std(data_set.values())})


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
    logging.basicConfig(level=logging.INFO)
    main()
