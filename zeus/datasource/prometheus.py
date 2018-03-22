import logging
import requests
import csv
from data_model import DataModel

# Create a metric to track time spent and requests made.
# REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
QUERY_API = "/api/v1/query"
RANGE_QUERY_API = "/api/v1/query_range"


class PrometheusAPI(DataModel):
    """Prometheus api client"""
    def __init__(self):
        self._query_api = QUERY_API
        self._range_query_api = RANGE_QUERY_API

    def query(self, data_source, query):
        data_set = dict()

        response = requests.get(data_source.url + self._range_query_api,
                                params={'query': query.expr, 'start': query.start_time,
                                        'end': query.end_time, 'step': query.step})
        status = response.json()['status']

        if status == "error":
            logging.error(response.json())
            return

        results = response.json()['data']['result']
        if len(results):
            for value in results[0]['values']:
                data_set[value[0]] = value[1]

        return data_set


class PrometheusQuery(object):
    def __init__(self, expr, start_time, end_time, step):
        self.expr = expr
        self.start_time = start_time
        self.end_time = end_time
        self.step = step


def write2csv(filename, model, ids, data_set):
    with open(filename, model) as f:
        writer = csv.writer(f)
        # for timestamp in sorted(data_set.keys(), reverse=True):
        #    writer.writerow([timestamp] + data_set[timestamp])
        # writer.writeheader()
        for data in data_set.values():
            writer.writerow([ids, data])








