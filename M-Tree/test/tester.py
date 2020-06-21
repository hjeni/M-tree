import logging
import time
from pathlib import Path
import concurrent.futures as futures

from mtree.mtree import MTree
from test.engine import parser
from test.engine.generator import Generator
from test._config import *
from mtree.heuristics import *

# logging setup encapsulation
LoggingSetup = namedtuple('LoggingSetup', 'format level new_line')


def _run_as_worker(f):
    """
    Simple decorator, runs function in a worker thread
    """
    def inner(*args, **kwargs):
        with futures.ThreadPoolExecutor() as executor:
            # run the function
            future = executor.submit(f, *args, **kwargs)
            # return the result
            return future.result()
    return inner


class Tester:
    """
    Tests all algorithms
    """

    def __init__(self):
        # logger setup
        self._logger = None
        form = '[%(name)s]: %(message)s'
        console = LoggingSetup(format=form, level=logging.INFO, new_line=False)
        file = LoggingSetup(format=form, level=logging.DEBUG, new_line=False)
        filename = self._get_logs_filename()
        self._init_logger(console, file, filename)

    def test_add_remove(self):
        """
        Tests data insertion & deletion from an M-Tree
        :return: success
        """
        success_add = True
        success_remove = True
        self._logger.info('Testing Mtree.add() & MTree.delete()\n')
        # loop all tests
        fng = Generator().data_file_name_generator()
        for i in range(TESTS_NUM):
            # do one test
            dataset = parser.read_dataset(PATH_TEST + next(fng))
            mtree = MTree()
            # (1) add
            test_ok = True
            for data in dataset:
                if not mtree.add(data):
                    # insertion wasn't successful
                    test_ok = False
                    success_add = False
            # log result
            self._logger.debug(f'Insertion test {i}: {test_ok}\n')
            # (2) remove
            test_ok = True
            for data in dataset:
                if not mtree.delete(data):
                    # deleting wasn't successful
                    test_ok = False
                    success_remove = False
                    break
            # log result
            self._logger.debug(f'Deletion test {i}:  {test_ok}\n')

        self._logger.info(f'TEST RESULT - add: {self._get_result_str(success_add)}'
                          f' | remove: {self._get_result_str(success_remove)}\n')
        return success_add, success_remove

    def time_test_all(self):
        """
        Repeatedly tries all split heuristics, measures time of insertion and queries
        """
        self._logger.info('testing time performance..\n')
        # test all 3 heuristics
        self._time_test_heuristic(split_data_random)
        self._time_test_heuristic(split_data_perfect)
        self._time_test_heuristic(split_data_smart)

    def time_test_random(self):
        """
        Tests random split heuristic, measures time of inserting and querying
        :return: insertion average time, query average time
        """
        return self._time_test_heuristic(split_data_random)

    def time_test_perfect(self):
        """
        Tests perfect split heuristic, measures time of inserting and querying
        :return: insertion average time, query average time
        """
        return self._time_test_heuristic(split_data_perfect)

    def time_test_smart(self):
        """
        Tests smart split heuristic, measures time of inserting and querying
        :return: insertion average time, query average time
        """
        return self._time_test_heuristic(split_data_smart)

    @_run_as_worker
    def _time_test_heuristic(self, split_h) -> (float, float):
        """
        Tests insertion & querying using passed split heuristic
        :param split_h: split heuristic function
        :return: insertion average time, query average time
        """
        t_add_sum, t_query_sum = 0, 0
        # file paths generators
        fng_add = Generator().data_file_name_generator()
        # go through all insertion tests
        self._logger.debug(f'starting insertion time test for {split_h}\n')
        for i in range(TESTS_NUM):
            # init M-Tree, add data
            dataset = parser.read_dataset(PATH_TEST + next(fng_add))
            # measure insertion time
            mtree, t_add = self._measure_time(self._init_mtree, dataset, split_h)
            t_add_sum += t_add
            self._logger.debug(f'time test INSERT {i}: {t_add:.4f}s\n')
            # measure queries
            _, t_query = self._measure_time(self._query_tree, mtree)
            t_query_sum += t_query
            self._logger.debug(f'time test QUERY {i}:  {t_query:.4f}s\n')
        # return average times
        t_add_avg, t_query_avg = t_add_sum / TESTS_NUM, t_query_sum / TESTS_NUM
        self._logger.info(f'TIME TEST RESULT: add: {t_add_avg:.4f}s, query: {t_query_avg:.4f}s\n')
        return t_add_avg, t_query_avg

    @staticmethod
    def _query_tree(tree: MTree):
        """
        Tests time of querying an M-Tree
        :param tree: M-Tree to be queried
        :return: time
        """
        fng_r_q = Generator().range_q_file_name_generator()
        fng_knn_q = Generator().knn_q_file_name_generator()
        # go through all query files
        for i in range(QUERY_NUM):
            # range queries
            queries = parser.read_query_range(PATH_TEST + next(fng_r_q))
            # perform all queries
            for r, data in queries:
                tree.range_query(data, r)
            # knn queries
            queries = parser.read_query_knn(PATH_TEST + next(fng_knn_q))
            # perform all queries
            for k, data in queries:
                tree.knn_query(data, k)

    @staticmethod
    def _init_mtree(data_it, split_h):
        """
        Initializes M-Tree with data
        :param data_it: iterator to the data
        :param split_h: split heuristic function
        :return: new M-Tree
        """
        mtree = MTree(split_function=split_h)
        # add data one by one
        for data in data_it:
            mtree.add(data)
        return mtree

    @staticmethod
    def _measure_time(f, *args, **kwargs):
        """
        Measures functions time performance
        :param f: function
        :param args: function args
        :param kwargs: function kwargs
        :return: return value of f, execution time
        """
        start = time.time()
        # run function
        rv = f(*args, **kwargs)
        # count time
        return rv, time.time() - start

    def _init_logger(self, console_setup=None, file_setup=None, filename='logs.txt'):
        """
        Initializes a logger for testing
        :param console_setup: console logging setup
        :param file_setup: file logging setup
        :param filename: path to a file for logging
        """
        self._logger = logging.getLogger(__name__)
        # set levels for both file and console
        # (1) console
        if console_setup is not None:
            # init handler
            handler = logging.StreamHandler()
            handler.setLevel(console_setup.level)
            handler.setFormatter(logging.Formatter(console_setup.format))
            # new line
            if not console_setup.new_line:
                handler.terminator = ''
            # add it
            self._logger.addHandler(handler)
        # (2) files
        if file_setup is not None:
            # init handler
            open(filename, 'w').close()
            handler = logging.FileHandler(filename)
            handler.setLevel(file_setup.level)
            handler.setFormatter(logging.Formatter(file_setup.format))
            # new line
            if not console_setup.new_line:
                handler.terminator = ''
            # add it
            self._logger.addHandler(handler)
        self._logger.setLevel(logging.DEBUG)

    @staticmethod
    def _generate_filename(num: int):
        """
        :return: filename containing 'num'
        """
        return PATH_LOG + FILENAME_LOG + str(num) + FILE_FORMAT_LOG

    def _get_logs_filename(self):
        """
        :return: Unused filename
        """
        # start with zero
        n = 0
        filename = self._generate_filename(n)
        while Path(filename).is_file():
            # try next number
            n += 1
            filename = self._generate_filename(n)
        return filename

    @staticmethod
    def _get_result_str(result):
        return 'ok' if result else 'failed'
