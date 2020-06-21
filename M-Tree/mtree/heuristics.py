"""
    Definitions of split heuristics functions, distance functions for metric space etc.
"""
import itertools
import math
from collections import namedtuple
import random

# infinity placeholders
INFINITY = float('inf')
# default capacity of all nodes
CAPACITY_DFLT = 100

# used for initialization of algorithms
DataPartition = namedtuple("DataPartition", "center r entries")
# represents data and its distance to queried object
# (so the data can be sorted by the distance)
SortableData = namedtuple('SortableData', 'data d')


def split_data_random(dataset: dict) -> (DataPartition, DataPartition):
    """
    Randomly splits data stored in dictionary into two parts
    :param dataset: dictionary of routing objects to be split
    :return: two new partitions
    """
    assert len(dataset) >= 4

    # shuffle keys
    keys = list(dataset.keys())
    random.shuffle(keys)
    # split data in half
    mid_idx = len(dataset) // 2
    entries = (dict(list(dataset.items())[:mid_idx]), dict(list(dataset.items())[mid_idx:]))
    # get center for each partition
    centers = _get_center_basic(entries[0], entries[1])
    # get radius for each partition
    rs = _get_rs(centers, entries)

    # update parent distances
    _update_parent_dist_all(centers[0], entries[0])
    _update_parent_dist_all(centers[1], entries[1])

    # create the partitions
    return DataPartition(centers[0], rs[0], entries[0]), DataPartition(centers[1], rs[1], entries[1])


def _update_parent_dist_all(center, to_update: dict):
    """
    Updates parent distances of all elements in a ball
    :param center: new center of the ball
    :param center: all elements in the ball
    """
    for key in to_update:
        to_update[key].parent_dist = dist_euclidean(key, center)


def _get_center_basic(*datasets):
    """
    :return: center for each dataset
    """
    centers = []
    for dataset in datasets:
        # simply mark the first element as center
        centers.append(list(dataset.keys())[0])
    return tuple(centers)


def _get_rs(centers, entries):
    """
    :return: radius for each center & partition entries pair
    """
    assert len(centers) == len(entries)

    rs = []
    # count radius pair after pair
    for center, entries in zip(centers, entries):
        rs.append(_calc_radius(center, entries))
    return tuple(rs)


def _calc_radius(center, others):
    """
    Calculates radius of a partition
    :param center: center of the ball
    :param others: all entries of the ball
    :return: calculated distance
    """
    r = 0
    # go through all entries
    for rt_data in others:
        # adjust radius if necessary
        d = dist_euclidean(center, rt_data)
        r = max(r, d + others[rt_data].r)
        others[rt_data].parent_dist = d
    return r


def split_data_perfect(dataset: dict) -> (DataPartition, DataPartition):
    """
    Compares all the data, find smallest overlap of new data balls
    best precision, worst speed
    :param dataset: dictionary of routing objects to be split
    :return: two new partitions
    """
    assert len(dataset) >= 4

    best = None
    intersect_min = INFINITY
    # go through all possible splits
    for partitions in _generate_splits(dataset):
        # quick fix
        if abs(len(partitions[0]) - len(partitions[1])) > 1:
            continue
        intersect_curr = _count_intersect_simple(*partitions)
        # update best
        if intersect_curr < intersect_min:
            intersect_min = intersect_curr
            best = partitions

    # update parent distances
    _update_parent_dist_all(best[0].center, best[0].entries)
    _update_parent_dist_all(best[1].center, best[1].entries)

    return best


def _generate_splits(dataset: dict) -> (DataPartition, DataPartition):
    """
    Generates all data splits into two partitions
    :param dataset: data dictionary
    :return: yields all data split combinations (lexicographically)
    """
    # go through all combinations
    for entries in _gen_comb_lex(dataset):
        # quick fix: only work with splits in half
        if abs(len(entries[0]) - len(entries[1])) > 1:
            continue
        # count center and radius for both partitions
        center_1, r_1 = _find_best_center(list(entries[0].keys()))
        center_2, r_2 = _find_best_center(list(entries[1].keys()))
        # yield new partitions
        yield DataPartition(center_1, r_1, entries[0]),  DataPartition(center_2, r_2, entries[1])


def _gen_comb_lex(dataset: dict):
    """
    Generates all combinations of splits into two parts
    :param dataset: dictionary of entries
    :return: yields pair of dictionaries containing the entries
    """
    # convert to list
    as_list = list(dataset.items())
    # count number of combinations to be yielded
    # (there are 2^n combinations, we count symmetric pairs as 1 -> 2^n-1 combinations)
    combinations_num = 2 ** (len(as_list) - 1)
    # generate all combinations
    for counter, pattern in enumerate(itertools.product([True, False], repeat=len(as_list))):
        # all combinations have been yielded
        if counter >= combinations_num:
            break
        else:
            # create the pair of dictionaries
            split_pair = dict([data for tf, data in zip(pattern, as_list) if tf]), \
                         dict([data for tf, data in zip(pattern, as_list) if not tf])
            # there have to be at least two elements in each part
            if len(split_pair[0]) >= 2 and len(split_pair[1]) >= 2:
                yield split_pair


def _find_best_center(dataset: list):
    """
    Finds best entry to represent the center of a nested ball
    :param dataset: data list
    :return: center entry, radius of the ball
    """
    # distances between two data parts that are already known
    distances = {}
    # init the dictionary
    for data in dataset:
        distances[data] = {}

    best = None
    r_min = INFINITY
    # go through data
    for data in dataset:
        r_curr = -INFINITY
        # compare to all data
        for child in dataset:
            # don't count distance second time
            if data in distances and child in distances[data]:
                d = distances[data][child]
            else:
                # count distance
                d = dist_euclidean(data, child)
                # memoize it
                distances[data][child] = d
                distances[child][data] = d
            # update r
            if data != child:
                r_curr = max(r_curr, d)
        # update best
        if r_curr < r_min:
            r_min = r_curr
            best = data
    # ideal center is now in best
    return best, r_min


def _count_intersect_simple(a: DataPartition, b: DataPartition) -> float:
    """
    Counts are of intersection of two circles
    Simplified heuristics for N-sphere intersection, works just as good
    :param a: first circle
    :param b: second circle
    :return: area of intersection
    """
    # source: https://www.xarg.org/2016/07/calculate-the-intersection-area-of-two-circles/

    # count distance between the centers
    d = dist_euclidean(a.center, b.center)
    # check if they intersect
    if d >= abs(a.r + b.r) or a.r == 0 or b.r == 0:
        # they don't
        return 0
    # they do, count the area
    a_sq = a.r**2
    b_sq = b.r**2
    if d <= abs(a.r - b.r):
        # simple, one circle inside another
        return math.pi * min(a_sq, b_sq)
    # more complicated, magic formula
    x = (a_sq - b_sq + d**2) / (d * 2)
    z = x**2
    y = math.sqrt(abs(a_sq - z))
    s = math.sqrt(abs(z + b_sq - a_sq))

    # handle ValueErrors caused by float comparison precision
    try:
        asin_a = math.asin(y / a.r)
    except ValueError:
        asin_a = _asin_safe(y / a.r)
    try:
        asin_b = math.asin(y / b.r)
    except ValueError:
        asin_b = _asin_safe(y / b.r)

    return a_sq * asin_a + b_sq * asin_b - y * (x + s)


def _asin_safe(x):
    """
    Counts arc sin of x, solves ValueErrors caused by float comparison
    """
    pi_2 = math.pi / 2
    # x is probably something like 1.00002 or -1.00002
    return pi_2 if x > 1 else -pi_2


def split_data_smart(dataset: dict) -> (DataPartition, DataPartition):
    """
    Picks two anchors, then adds each data from the dataset to the closer one
    compromise between the speed and the complexity (keeps complexity = O(n))
    Resulting data partitions can be under-flowed
    :param dataset: dictionary of routing objects to be split
    :return: two new partitions
    """
    assert len(dataset) >= 4

    # pick anchors
    center_min, center_max = _find_centers_opposite(dataset)
    # distribute data between the anchors
    entries_min, entries_max = {}, {}
    r_min, r_max = 0, 0
    for data in dataset:
        d_min = dist_euclidean(center_min, data)
        d_max = dist_euclidean(center_max, data)
        # pick closer anchor
        if d_min < d_max:
            # update radius, add entry
            r_min = max(r_min, d_min)
            entries_min[data] = dataset[data]
            entries_min[data].parent_dist = d_min
        else:
            # update radius, add entry
            r_max = max(r_max, d_max)
            entries_max[data] = dataset[data]
            entries_max[data].parent_dist = d_max

    # update parent distances
    _update_parent_dist_all(center_max, entries_max)
    _update_parent_dist_all(center_min, entries_min)
    # create data partition for each anchor
    return DataPartition(center_min, r_min, entries_min), DataPartition(center_max, r_max, entries_max)


def _find_centers_opposite(dataset: dict) -> tuple:
    """
    Finds centers with lowest / highest summary of elements in the data
    :param dataset: data dictionary
    :return: lowest, highest
    """
    sum_min, sum_max = INFINITY, -INFINITY
    center_min, center_max = None, None
    # go through dataset
    for data in dataset:
        sum_data = sum(data)
        # update min & max
        if sum_data < sum_min:
            sum_min = sum_data
            center_min = data
        if sum_data > sum_max:
            sum_max = sum_data
            center_max = data

    return center_min, center_max


def dist_euclidean(a, b):
    """
    :return: Euclidean distance between two objects a & b
    """
    assert len(a) == len(b)
    d_squared = 0
    for v1, v2 in zip(a, b):
        # add power of two to the final squared distance
        diff = v1 - v2
        d_squared += diff ** 2
    # return square root of the distance squared
    return math.sqrt(d_squared)
