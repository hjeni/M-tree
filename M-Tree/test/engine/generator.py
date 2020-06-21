"""
Simple engine engine
"""

import logging
import os
import random
from test._config import *


class Generator:
    """
    Generates simple metric test data (tuples)
    """
    def __init__(self):
        # init a logger (console logging only is enough for the generator)
        self._logger = logging.getLogger(__name__)
        # init handler
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('[%(name)s]: %(message)s'))
        # add it
        self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)

    @staticmethod
    def _gen_tuple_int(dim: int, val_min: int, val_max: int):
        """
        :param dim: dimension of the tuple
        :param val_min: minimal value which can occur in the tuple
        :param val_max: maximal value which can occur in the tuple
        :return: random tuple
        """
        return tuple(random.randint(val_min, val_max) for _ in range(dim))

    def gen_data_file(self, dir_path: str, file_name: str, lines: int = DFLT_SIZE_DATA,
                      dim: int = DFLT_DIM, val_min: int = DFLT_MIN_VALUE, val_max: int = DFLT_MAX_VALUE):
        """
        Generates test data for MAMs testing
        Format: 1 tuple of integers per line, all elements divided by space (e.g. '1 2 3 4')
        :param dir_path: path to a directory to generate the file at
        :param file_name: name of generated file
        :param lines: number of records to be generated
        :param dim: dimension of the tuple
        :param val_min: minimal value which can occur in the tuple
        :param val_max: maximal value which can occur in the tuple
        """
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        # create new file
        file_path = dir_path + file_name
        try:
            with open(file_path, 'w') as f:
                # generate engine
                for _ in range(lines):
                    # generate tuple
                    t = self._gen_tuple_int(dim, val_min, val_max)
                    t = [str(x) for x in t]
                    # write tuple
                    line = ' '.join(t)
                    print(line, file=f)
        except FileNotFoundError:
            self._logger.info('could not generate data!')
            return
        # everything ok
        self._logger.info(f'data generated - location: "{file_path}" size: {lines} (rows) x {dim} (dimensions)')

    @staticmethod
    def data_file_name_generator():
        """
        Generates filenames for the test data
        """
        counter = 0
        while True:
            yield FILENAME_TEST_DATA + str(counter) + FILE_FORMAT_TEST
            counter += 1

    def gen_range_q_file(self, dir_path: str, file_name: str, lines: int = DFLT_SIZE_QUERY,
                         dim: int = DFLT_DIM, val_min: int = DFLT_MIN_VALUE, val_max: int = DFLT_MAX_VALUE):
        """
        Generates range queries for MAMs testing
        Format: range as integer + 1 tuple of integers per line, all elements divided by space (e.g. '69 1 2 3 4')
        :param dir_path: path to a directory to generate the file at
        :param file_name: name of generated file
        :param lines: number of records to be generated
        :param dim: dimension of the tuple
        :param val_min: minimal value which can occur in the tuple
        :param val_max: maximal value which can occur in the tuple
        """
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        # create new file
        file_path = dir_path + file_name
        # querying whole database is not pretty common
        range_min = 0
        range_max = abs(val_min - val_max) // 10
        try:
            with open(file_path, 'w') as f:
                # generate engine
                for _ in range(lines):
                    # generate range
                    r = random.randint(range_min, range_max)
                    # generate tuple
                    t = self._gen_tuple_int(dim, val_min, val_max)
                    t = [str(x) for x in t]
                    # write range
                    line = str(r) + ' '
                    # write tuple
                    line += ' '.join(t)
                    print(line, file=f)
        except FileNotFoundError:
            self._logger.info(f'could not generate range query!')
            return
        # debug
        self._logger.info(f'range query generated - location: "{file_path}" size: {lines} (rows) X {dim} (dimensions)')

    @staticmethod
    def range_q_file_name_generator():
        """
        Generates filenames for the range queries
        """
        counter = 0
        while True:
            yield FILENAME_TEST_RANGE_Q + str(counter) + FILE_FORMAT_TEST
            counter += 1

    def gen_knn_q_file(self, dir_path: str, file_name: str, k_min: int, k_max: int, lines: int = DFLT_SIZE_QUERY,
                       dim: int = DFLT_DIM, val_min: int = DFLT_MIN_VALUE, val_max: int = DFLT_MAX_VALUE):
        """
        Generates knn queries for MAMs testing
        Format: k as integer + tuple of integers per line, all elements divided by space (e.g. '69 1 2 3 4')
        :param dir_path: path to a directory to generate the file at
        :param file_name: name of generated file
        :param k_min: minimal k which can be generated
        :param k_max: maximal k which can be generated
        :param lines: number of records to be generated
        :param dim: dimension of the tuple
        :param val_min: minimal value which can occur in the tuple
        :param val_max: maximal value which can occur in the tuple
        """
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        # create new file
        file_path = dir_path + file_name
        # querying whole database is not pretty common
        try:
            with open(file_path, 'w') as f:
                # generate engine
                for _ in range(lines):
                    # generate range
                    k = random.randint(k_min, k_max)
                    # generate tuple
                    t = self._gen_tuple_int(dim, val_min, val_max)
                    t = [str(x) for x in t]
                    # write range
                    line = str(k) + ' '
                    # write tuple
                    line += ' '.join(t)
                    print(line, file=f)
        except FileNotFoundError:
            self._logger.info('could not generate knn query!')
            return
        # everything ok
        self._logger.info(f'knn query generated - location: "{file_path}" size: {lines} (rows) X {dim} (dimensions)')

    @staticmethod
    def knn_q_file_name_generator():
        """
        Generates filenames for the knn queries
        """
        counter = 0
        while True:
            yield FILENAME_TEST_KNN_Q + str(counter) + FILE_FORMAT_TEST
            counter += 1


