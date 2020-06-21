from mtree._entries import RoutingEntry, GroundEntry
from mtree._nodes import Root, Leaf, Router
from mtree.heuristics import *


class MTree:
    """
    Represents M-Tree data structure
    """

    def __init__(self, capacity_max: int = 9, dist_function=dist_euclidean, split_function=split_data_random):
        """
        :param capacity_max: maximal number of objects any node can store
        :param dist_function: metrics used to determine distance of 2 data objects, default is euclidean distance
        has to take two parameters (data) and return distance between them
        :param split_function: split heuristics function, default split heuristics is random split
        has to take dictionary and return two data partitions
        """
        self._root = None
        self.capacity_min = 2
        self.capacity_max = capacity_max
        self.split_function = split_function
        self._dist_function = dist_function

    def __str__(self):
        # just display the root
        return f'M-Tree: < {self._root} >'

    def add(self, data):
        """
        Adds new data into the M-Tree
        :param data: data to be inserted
        :return: success
        """
        # tree might be empty
        if self._root is None:
            # init the root with first entry
            self._init_root(data)
            return True
        else:
            # try to add data to the existing root node
            if self._root.add(data):
                # check root capacity
                if self._root.is_overflowed(max_capacity=self.capacity_max):
                    # add one level to the tree
                    self._split_root()
                return True
            # couldn't add data
            return False

    def delete(self, data):
        """
        Removes an object containing passed data from the M-Tree
        :param data: data to be removed
        :return: success
        """
        # tree might be empty
        if self._root is None:
            return False
        # try to delete the data
        if self._root.delete(data):
            if self._root.is_underflowed(min_capacity=1):
                self._root = None
            return True
        # couldn't delete data
        return False

    def range_query(self, data, r):
        """
        Finds all object within the range from the data object
        :param data: query object data
        :param r: query range
        :return: list of r-similar objects
        """
        # tree might be empty
        if self._root is None:
            return []
        # count distance to the root
        d = self._dist_function(data, self._root.data)
        # simply run search from the root
        return self._root.search(data=data, d_parent=d, r=r)

    def knn_query(self, data, k):
        """
        Finds k objects closest to the queried one
        :param data: query object data
        :param k: number of closest neighbours to be found
        :return: list of k (or less, in case there is not enough objects) most similar objects
        """
        # tree might be empty
        if self._root is None:
            return []
        # count distance to the root
        d = self._dist_function(data, self._root.data)
        # simply run search from the root
        return self._root.search(data=data, d_parent=d, r=INFINITY, k=k)

    def _init_root(self, data):
        """
        Initializes root of the M-Tree, creates nodes to store the first record
        :param data: initial data
        """
        # (1) Leaf & its ground entry
        # create ground object, add it to a dictionary
        ground = {data: GroundEntry(data=data)}
        # create first leaf, add ground object(s) to it
        leaf = Leaf(entries=ground,
                    data=data,
                    dist_function=self._dist_function,
                    split_function=self.split_function,
                    capacity=self.capacity_max)
        # (2) Router & its routing entry
        # create routing object, add it to a dictionary
        routing = {data: RoutingEntry(subtree=leaf, data=data)}
        # create root, add rooting object(s) to it
        self._root = Root(entries=routing,
                          data=data,
                          dist_function=self._dist_function,
                          split_function=self.split_function,
                          capacity=self.capacity_max,
                          r=INFINITY)

    def _split_root(self):
        """
        Splits root node into two new nodes, which both become subtrees of a new root
        New root will have center in the center of first subtree
        """

        # split all routing entries into two partitions
        partitions = self._root.get_split_data()

        # create new root with 2 new rooting entries
        entries = {}
        # (1) create first router and its routing entry
        router = Router(entries=partitions[0].entries,
                        data=partitions[0].center,
                        dist_function=self._dist_function,
                        split_function=self.split_function,
                        capacity=self.capacity_max,
                        r=partitions[0].r)
        entries[partitions[0].center] = RoutingEntry(subtree=router,
                                                     data=partitions[0].center,
                                                     r=partitions[0].r)
        # (2) create second router and its routing entry
        router = Router(entries=partitions[1].entries,
                        data=partitions[1].center,
                        dist_function=self._dist_function,
                        split_function=self.split_function,
                        capacity=self.capacity_max,
                        r=partitions[1].r)
        parent_dist = self._dist_function(partitions[0].center, partitions[1].center)
        entries[partitions[1].center] = RoutingEntry(subtree=router,
                                                     data=partitions[1].center,
                                                     r=partitions[1].r,
                                                     parent_dist=parent_dist)
        # count distance between centers
        d_centers = self._dist_function(partitions[0].center, partitions[1].center)
        # count root's new radius
        root_r = max(partitions[0].r, d_centers + partitions[1].r)
        # finally create the root
        self._root = Root(entries=entries,
                          data=partitions[0].center,
                          dist_function=self._dist_function,
                          split_function=self.split_function,
                          r=root_r)
