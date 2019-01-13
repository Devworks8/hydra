from collections import MutableMapping


def flatten_dict(d, parent_key='', sep='_'):
    """
    Flattens nested dictionary.
    :param d: nested dictionary
    :param parent_key: root key
    :param sep: separator to use
    :return: flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
