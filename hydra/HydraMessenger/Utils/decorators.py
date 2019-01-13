import functools
from collections import MutableMapping

from deepmerge import always_merger
from hydra.HydraMessenger.Utils.flatten_dict import flatten_dict as _flatten_dict


def singleton(cls):
    """
    Make a class a Singleton class (only one instance)
    :param cls: Class
    :return: cls singleton
    """
    @functools.wraps(cls)
    def wrapper_singleton(*args, **kwargs):
        if not wrapper_singleton.instance:
            wrapper_singleton.instance = cls(*args, **kwargs)
        return wrapper_singleton.instance
    wrapper_singleton.instance = None
    return wrapper_singleton


def inflate_dict(sep):
    def decorator_inflate_dict(func):
        @functools.wraps(func)
        def wrapper_inflate_dict(*args, **kwargs):
            settings = func(*args, **args)
            results = {}
            for k, v in settings.items():
                result = ''
                cap = 0
                for word in k.split(kwargs['sep']):
                    result += "{" + "'{}': ".format(word)
                    cap += 1
                result += "'{}'".format(v) + "}" * cap
                results = always_merger.merge(results, eval(result))
            return results
        return wrapper_inflate_dict
    return decorator_inflate_dict


def flatten_dict(parent_key, sep):
    def decorator_flatten_dict(func):
        @functools.wraps(func)
        def wrapper_flatten_dict(*args, **kwargs):
            settings = func(*args, **kwargs)
            items = []
            for k, v in settings.items():
                new_key = parent_key + sep + k if parent_key else k
                if isinstance(v, MutableMapping):
                    items.extend(_flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)

        return wrapper_flatten_dict
    return decorator_flatten_dict

