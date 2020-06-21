import itertools


def convert_safe(value, t: type = int):
    """
    Tries to convert value to specified type
    :param value: Value to be converted
    :param t: type of conversion (int is default)
    :return: converted value when successful, None otherwise
    """
    try:
        return t(value)
    except (ValueError, TypeError):
        return None


def try_convert_seq(text: str, t: type = int, delim: str = None) -> tuple:
    """
    Tries to convert values separated by delimiter to one common type
    :param text: string of values separated by the delimiter
    :param t: type of conversion (int is default)
    :param delim: delimiter (any whitespace is default)
    :return: list of converted elements (each element either converted or None when the conversion was not successful)
    """
    # split single elements
    if delim is None:
        split = [x for x in text.split() if x != '']
    else:
        split = [x for x in text.split(delim) if x != '']
    # convert each value separately
    return tuple(map(convert_safe, split, itertools.repeat(t)))


def read_dataset(path: str):
    """
    Generates data from a file
    :param path: path to the dataset file
    :return: iterator to the data
    """
    # open the file
    with open(path, 'r') as f:
        for line in f:
            data = try_convert_seq(text=line)
            yield data


def read_query_range(path: str):
    """
    Generates range queries from a file
    :param path: path to the query file
    :return: iterator to a pair: range, data
    """
    # open the file
    with open(path, 'r') as f:
        for line in f:
            data = try_convert_seq(text=line)
            yield data[0], data[1:]


def read_query_knn(path: str):
    """
    Generates knn queries from a file
    :param path: path to the query file
    :return: iterator to a pair: k, data
    """
    # open the file
    with open(path, 'r') as f:
        for line in f:
            data = try_convert_seq(text=line)
            yield data[0], data[1:]

