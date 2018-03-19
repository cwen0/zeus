from prometheus import PrometheusAPI
from prometheus import Query
from prometheus import write2csv
import logging
import csv
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
import seaborn as sns

from tsfresh import extract_features
from tsfresh.utilities.dataframe_functions import make_forecasting_frame
from sklearn.ensemble import AdaBoostRegressor
from tsfresh.utilities.dataframe_functions import impute
from tsfresh.utilities.dataframe_functions import roll_time_series
from tsfresh.feature_extraction import ComprehensiveFCParameters


def main():
    query = Query("sum(rate(tidb_server_query_total[1m])) by (status)", "2018-03-16T12:10:30.781Z",
                  "2018-03-16T13:11:00.781Z", "60s")
    api = PrometheusAPI()
    data_set = api.range_query("http://172.16.10.4:30943", query)

    # print(data_set)
    for index in range(1, 3):
        write2csv("train.csv", 'a+', index, data_set)
    csvFile = open("train.csv", "r")
    reader = csv.reader(csvFile)
    ids = []
    values = []
    for item in reader:
        ids.append(item[0])
        values.append(float(item[1]))

    df = pd.DataFrame({"id": ids, "value": values[:len(ids)]})
    print(df)
    extraction_settings = ComprehensiveFCParameters()
    x = extract_features(df, column_id="id", column_value="value",
                         impute_function=impute, default_fc_parameters=extraction_settings)
    x.head()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
