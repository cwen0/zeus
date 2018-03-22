# -*- coding: utf-8 -*-

import argparse
import sys
from models.iforest import IForest

QUERY_QPS_EXPR = "sum(rate(tidb_server_query_total[1m])) by (status)"


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

    ilf = IForest(QUERY_QPS_EXPR, kwargs["data_url"])
    ilf.run()




