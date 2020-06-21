"""
Utility functions used to generate test data
Uses test.engine.generator.Generator class to generate the data
"""

import glob
import os

from test._config import *
from test.engine.generator import Generator


# config
DIMENSIONS = 2
LINES_TEST = 500
LINES_Q = 20
K_RANGE = (1, 100)


def generate_data():
    """
    Data generation entry function
    """
    # delete previous content
    _clear()
    # generate new data
    _generate_data()
    # generate new queries
    _generate_queries_range()
    _generate_queries_knn()


def _clear():
    """
    Removes all test files generated (except of 'sample_data.txt')
    :return: success
    """
    try:
        # delete all files one by one
        files = glob.glob(PATH_TEST + '*.txt')
        for f in files:
            os.unlink(f)
    except OSError:
        return False
    return True


def _generate_data():
    """
    Generates new data
    """
    fng = Generator().data_file_name_generator()
    for i in range(TESTS_NUM):
        # set up
        filename = next(fng)
        # generate
        Generator().gen_data_file(PATH_TEST, filename, lines=LINES_TEST, dim=DIMENSIONS)


def _generate_queries_range():
    """
    Generates new range queries
    """
    fng = Generator().range_q_file_name_generator()
    for i in range(QUERY_NUM):
        # set up
        filename = next(fng)
        # generate
        Generator().gen_range_q_file(PATH_TEST, filename, lines=LINES_Q, dim=DIMENSIONS)


def _generate_queries_knn():
    """
    Generates new knn queries
    """
    fng = Generator().knn_q_file_name_generator()
    for i in range(QUERY_NUM):
        # set up
        filename = next(fng)
        # generate
        Generator().gen_knn_q_file(PATH_TEST, filename, k_min=K_RANGE[0],
                                   k_max=K_RANGE[1], lines=LINES_Q, dim=DIMENSIONS)
