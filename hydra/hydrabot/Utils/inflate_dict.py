from deepmerge import always_merger


def inflate_dict(d, sep='_'):
    """
    Expands flattened nested dictionary.
    :param d: flatten dictionary
    :param sep: separator used
    :return: nested dictionary
    """
    results = {}
    for k, v in d.items():
        result = ''
        cap = 0
        for word in k.split(sep):
            result += "{" + "'{}': ".format(word)
            cap += 1
        result += "'{}'".format(v) + "}" * cap
        results = always_merger.merge(results, eval(result))
    return results
