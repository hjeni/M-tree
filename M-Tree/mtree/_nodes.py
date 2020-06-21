"""
    Definitions of M-Tree nodes
"""

from mtree._entries import GroundEntry, RoutingEntry
from mtree.heuristics import *
from heapq import merge


class _Node:
    """
    Represents one m-tree node

    Abstract metric space object, contains set of other metric space objects (entries)
    """

    def __init__(self, entries, data, dist_function, split_function, r=0, capacity=CAPACITY_DFLT):
        """
        :param entries: dictionary of entries the node stores (can be None or empty)
        :param data: data defining node's position in the metric space
        :type dist_function: determines distance between two data objects
        :type split_function: function used to split the node in half in case of overflow
        :param r: range (radius)
        :param capacity: maximal number of entries the node can store
        """
        self.dist_function = dist_function
        self._entries = entries
        self.data = data
        self.split_function = split_function
        self.r = r
        self.capacity = capacity

    def __str__(self):
        """
        :return: Returns printable representation of the node
        """
        s = f'Node({len(self._entries)}): <'
        for i, e in enumerate(self._entries.values()):
            s += f'{i}: {e} '
        s += '>'
        return s

    def is_overflowed(self, max_capacity: int):
        """
        :param max_capacity: maximal number of records the node can contain
        :return: True when number of objects is higher than the capacity of the node, otherwise False
        """
        return len(self._entries) > max_capacity

    def is_underflowed(self, min_capacity: int = 2):
        """
        :param min_capacity: minimal number of records the node must contain
        :return: Returns true when there is less than two objects in the node, otherwise False
        """
        return len(self._entries) < min_capacity

    def get_split_data(self) -> (DataPartition, DataPartition):
        """
        :return: Two new partitions which together contain all the routing entries of the caller node
        """
        # split the routing objects into two partitions
        return self.split_function(self._entries)


class _NodeInternal(_Node):
    """
    Non-trivial node (Not a leaf, either root or router)
    """

    def add(self, data) -> bool:
        """
        Picks best routing object, adds data into its subtree
        :param data: data to be added
        :return: success
        """
        # pick routing object data fits into the best
        best = None
        # distance from the best node
        from_best = INFINITY
        # range the best node has to be adjusted to
        adjust = INFINITY

        # go through all routing objects
        for entry_key in self._entries:
            # calculate distance
            d = self.dist_function(data, entry_key)
            # calculate distance from routing entry's border
            if d - self._entries[entry_key].r > 0:
                # data object doesn't fit into current routing entry
                if best is None or (d < adjust and from_best == INFINITY):
                    best = self._entries[entry_key]
                    adjust = d
            else:
                # data object fits into current routing entry
                if best is None or d < from_best:
                    best = self._entries[entry_key]
                    from_best = d

        # best entry is now saved in 'best', no matter whether the data object fits into any routing entry or not
        if from_best == INFINITY:
            # data object doesn't fit, update r of the best node first
            best.node.r = adjust
            best.r = adjust
        # add to the best node found
        success = best.node.add(data)
        # check node capacity
        if best.node.is_overflowed(self.capacity):
            # split node into two
            self.balance_subtree_overflowed(best)
        return success

    def search(self, data, d_parent, r, k=INFINITY) -> list:
        """
        Searches all routing objects & find all objects with defined similarity to the data
        :param data: query data
        :param r: range (dissimilarity)
        :param d_parent: distance between the data and the parent node (self)
        :param k: maximum number of elements to search for
        :return: sorted list of all r-similar objects in this node with max size of k
        """
        in_range = []
        # go through all rooting objects
        for entry_key in self._entries:
            # try to avoid counting the distance by triangular comparison of distances to the parent
            d_diff = abs(self._entries[entry_key].parent_dist - d_parent)
            r_sum = r + self._entries[entry_key].r
            if d_diff <= r_sum:
                # count actual distance
                d = self.dist_function(data, entry_key)
                # check whether the subtree intersects with the query or not
                if d <= r_sum:
                    # add data from the subtree when it fits
                    dataset = self._entries[entry_key].node.search(data, d, r, k)
                    in_range = list(merge(in_range, dataset, key=lambda x: x.d))
        # filter unnecessary objects
        if len(in_range) > k:
            return in_range[:k]

        return in_range

    def balance_subtree_overflowed(self, ro: RoutingEntry):
        """
        Splits node using split heuristics into two new ones, distributes data between them
        :param ro: routing object (entry) pointing to the subtree which we want to balance
        """
        # split the data of node to be split
        partitions = ro.node.get_split_data()
        assert len(partitions) == 2

        # leave one partition at its place and just update parent, add second node

        """
        # (1) rewrite old routing entry with the first half
        ro.node = ro.node.get_split_node(entries=partitions[0].entries,
                                         r=partitions[0].r,
                                         data=partitions[0].center)
        ro.data = partitions[0].center
        ro.parent_dist = self.dist_function(self.data, partitions[0].center)
        ro.subtree_ptr = ro.node
        """
        # delete old entry
        del self._entries[ro.data]
        # create two new entries
        # (1)
        router_1 = ro.node.get_split_node(entries=partitions[0].entries,
                                          r=partitions[0].r,
                                          data=partitions[0].center)
        routing_entry_1 = RoutingEntry(subtree=router_1,
                                       data=partitions[0].center,
                                       r=partitions[0].r,
                                       parent_dist=self.dist_function(self.data, partitions[0].center))
        # update entries dictionary
        self._entries[partitions[0].center] = routing_entry_1
        # (2)
        router_2 = ro.node.get_split_node(entries=partitions[1].entries,
                                          r=partitions[1].r,
                                          data=partitions[1].center)
        routing_entry_2 = RoutingEntry(subtree=router_2,
                                       data=partitions[1].center,
                                       r=partitions[1].r,
                                       parent_dist=self.dist_function(self.data, partitions[1].center))
        # update entries dictionary
        self._entries[partitions[1].center] = routing_entry_2


class Root(_NodeInternal):
    """
    Represents root node of an M-Tree
    """

    def delete(self, data) -> bool:
        """
        Tries to delete the data from all subtrees the data would fit into
        :param data: data to be removed
        :return: Success
        """
        deleted = False
        # calculate distance
        d_root = self.dist_function(data, self.data)
        # try to delete the data from all subtrees
        for ro in self._entries:
            if self._entries[ro].node.delete(data, d_root):
                # deletion successful
                deleted = True
        return deleted

    # todo: handle 'donating'


class Router(_NodeInternal):
    """
    Represents routing node of an M-Tree
    """

    def delete(self, data, d_parent) -> bool:
        """
        Tries to delete the data from all subtrees the data would fit into
        :param data: data to be removed
        :param d_parent: distance between data and the parent node
        :return: Success
        """
        deleted = False
        # go through routing objects, try to delete from all subtrees
        for ro in self._entries:
            # calculate distance-to-root difference
            d_diff = abs(d_parent - self._entries[ro].parent_dist)
            # try to delete only when the data object has any chance to fit into the subtree
            if d_diff <= self._entries[ro].r:
                # count data object distance to current node
                d = self.dist_function(data, self._entries[ro].data)
                # check whether it actually fits in ot not, only remove from the subtree when it does
                if d <= self._entries[ro].r and self._entries[ro].node.delete(data, d):
                    # deletion successful
                    deleted = True
        return deleted

    def get_split_node(self, entries, r, data):
        """
        :return: Returns new router node with given parameters
        """
        return Router(entries=entries,
                      data=data,
                      dist_function=self.dist_function,
                      split_function=self.split_function,
                      capacity=self.capacity,
                      r=r)

    # todo: handle 'donating'


class Leaf(_Node):
    """
    Represents leaf node of an M-Tree
    """

    def add(self, data) -> bool:
        """
        Adds data to the node
        :param data: data to be added
        :return: Success
        """
        # don't add the data if it's already there
        if data in self._entries:
            return False
        # count distance between the data and the node
        d = self.dist_function(data, self.data)
        # add data
        self._entries[data] = GroundEntry(oid=0, data=data, parent_dist=d)
        # update node range if necessary
        if d > self.r:
            self.r = d
        return True

    def delete(self, data, parent_dist) -> bool:
        """
        Deletes data from the node
        :param parent_dist: distance to parent
        :param data: data to be removed
        :return: Success
        """
        # check
        if data not in self._entries:
            return False
        # delete
        del self._entries[data]
        return True

    def search(self, data, d_parent, r, k) -> list:
        """
        Searches all ground entries, looks for data with 'r' or lower dissimilarity
        :param data: query data
        :param r: range (dissimilarity)
        :param k: maximum number of elements to search for
        :param d_parent: distance between the data and the parent node (self)
        :return: sorted list of all r-similar objects in this node with max size of k
        """
        in_range = []
        # go through all ground objects
        for entry_key in self._entries:
            # try to avoid counting the distance by triangular comparison of distances to the parent
            d_diff = abs(self._entries[entry_key].parent_dist - d_parent)
            if d_diff <= r:
                # count actual distance
                d = self.dist_function(data, entry_key)
                # check whether the go fits into the query or not
                if d <= r:
                    # append when it fits
                    in_range.append(SortableData(data=entry_key, d=d))
        # sort the list first
        in_range.sort(key=lambda x: x.d)
        # filter unnecessary data when k is specified
        if len(in_range) > k:
            return in_range[:k]
        return in_range

    def get_split_node(self, entries, r, data):
        """
        :return: Returns new leaf node with given parameters
        """
        return Leaf(entries=entries,
                    data=data,
                    dist_function=self.dist_function,
                    split_function=self.split_function,
                    capacity=self.capacity,
                    r=r)

    # todo: handle 'donating'
