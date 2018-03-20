import numpy as np
import logging
from classification import ts_classifier


def main():
    train = np.genfromtxt('datasets/train.csv', delimiter='\t')
    test = np.genfromtxt('datasets/test.csv', delimiter='\t')
    classifier = ts_classifier()
    classifier.knn_predict(train, test, 4)
    classifier.performance(test[:, -1])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
