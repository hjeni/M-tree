"""
    Definitions of different metric objects
"""


class _Entry:
    """
    Represents any entry (either routing entry containing subtree pointer or a ground entry)
    more info about routing and ground entries:
    https://www.sciencedirect.com/science/article/pii/S1570866708000786#bib015
    """
    def __init__(self, data, r):
        """
        :param data: data defining entry's position in the metric space
        :param r: radius (range)
        """
        self.data = data
        self.r = r


class RoutingEntry(_Entry):
    """
    Represents routing entry in any non-leaf object
    """
    def __init__(self, subtree, data=None, r: float = 0, parent_dist: float = 0):
        """
        :type subtree: pointer to subtree node
        :param data: metric data
        :param r: radius (range)
        :param parent_dist: distance to parent
        """
        super(RoutingEntry, self).__init__(data, r)
        self.parent_dist = parent_dist
        self.node = subtree

    def __str__(self):
        # display only the subtree
        return str(self.node)


class GroundEntry(_Entry):
    """
    Represents ground entry in leafs
    """

    def __init__(self, oid=0, data=None, r: float = 0, parent_dist: float = 0):
        """
        Initializes new instance of ground entry object
        :param oid: external identifier of original object
        :param data: metric data
        :param r: radius (range)
        :param parent_dist: distance to parent
        """
        super(GroundEntry, self).__init__(data, r)
        self.oid = oid
        self.parent_dist = parent_dist

    def __str__(self):
        # display only the data
        return f'Ground: {self.data}'
