import matplotlib.pylab as plt
import seaborn as sns
from tsfresh.examples.robot_execution_failures import download_robot_execution_failures, load_robot_execution_failures
from tsfresh import extract_features, extract_relevant_features, select_features
from tsfresh.utilities.dataframe_functions import impute
from tsfresh.feature_extraction import ComprehensiveFCParameters
from sklearn.tree import DecisionTreeClassifier


class Feature():
    def __init__(self, data_set):
        self.data_set = data_set

    def extract_features(self):
        extraction_settings = ComprehensiveFCParameters()
        X = extract_features(df,
                             column_id='id', column_sort='times',
                             default_fc_parameters=extraction_settings,
                             impute_function=impute)

