"""
Handles M-Tree saving and loading using pickle module
"""
import os
import pickle

from mtree.mtree import MTree
from test.engine.generator import Generator
from test.engine import parser
from mtree.heuristics import *

# sample data config
PICKLE_DIR = 'pickled/'
PICKLE_FILE = 'sample.pkl'
PICKLE_PATH = PICKLE_DIR + PICKLE_FILE
SAMPLE_DATA_DIR = 'test/datasets/'
SAMPLE_DATA_FILE_NAME = 'sample_data.txt'
SAMPLE_DATA_LINES = 10000
SAMPLE_DATA_DIM = 3


def _pickle_mtree(mtree, path):
    """
    Serializes the M-Tree and pickles it into a file
    :type mtree: M-Tree to be pickled
    :param path: path to the pickle file (creates new one if it doesnt exist)
    """
    with open(path, mode='bw') as f:
        pickle.dump(mtree, f)


def _unpickle_mtree(path):
    """
    Loads M-Tree state from a pickle file
    :param path: path to the pickle file
    :return: deserialized M-Tree
    """
    with open(path, mode='br') as f:
        mtree = pickle.load(f)
    return mtree


def generate_pkl():
    """
    Generates pickle file to be loaded by a GUI app
    """
    # create new M-Tree
    mtree = MTree(split_function=split_data_smart)
    # generate sample data
    Generator().gen_data_file(SAMPLE_DATA_DIR, SAMPLE_DATA_FILE_NAME, SAMPLE_DATA_LINES, SAMPLE_DATA_DIM)
    # add the data to the tree
    for data in parser.read_dataset(SAMPLE_DATA_DIR + SAMPLE_DATA_FILE_NAME):
        mtree.add(data)
    # pickle the tree
    if not os.path.exists(PICKLE_DIR):
        os.mkdir(PICKLE_DIR)
    _pickle_mtree(mtree, PICKLE_PATH)


def save_to_pkl(mtree):
    """
    Saves M-Tree instance to a pickle file
    :param mtree: MTree instance
    """
    if not os.path.exists(PICKLE_DIR):
        os.mkdir(PICKLE_DIR)

    _pickle_mtree(mtree, PICKLE_PATH)


def load_from_pkl():
    """
    Loads M-Tree instance from a pickle file
    :return: M-Tree or None, when there is nothing to load
    """
    # check the path
    if not os.path.exists(PICKLE_PATH):
        return None
    return _unpickle_mtree(PICKLE_PATH)
