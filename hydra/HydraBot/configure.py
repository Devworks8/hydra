import os.path

from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from hydra.HydraBot.Utils.decorators import *
from hydra.HydraBot.Utils.inflate_dict import inflate_dict


# TODO: Finish error handling.
@singleton
class CfgManager:
    def __init__(self):
        self._DEFAULTS = self.__generate_defaults()
        self.settings = self.__load_settings()

    @flatten_dict(parent_key='', sep='_')
    def __load_settings(self):
        """
        Load settings from file, ifnotexist, create new file.
        :return: dictionary
        """
        if os.path.exists("./settings.yml") and os.stat("./settings.yml").st_size > 1:
            with open("./settings.yml") as settings:
                return load(settings)
        else:
            with open("./settings.yml", 'w') as _:
                dump(load(self._DEFAULTS), _, default_flow_style=False)

            return load(self._DEFAULTS)

    def __generate_defaults(self):
        """
        default config file template.
        :return: String
        """
        defaults = """
        service:
            proxy:
                host: '127.0.0.1'
                port: 33907
        views:
            client:
                crypto: True
                """

        return defaults

    def _find_header(self, header=None, value=None):
        """
        Locate key and value set.
        :param header: key to look for
        :param value: key's value to set
        :return: List of tuples
        """
        results = []
        for k, v in self.settings.items():
            if header in k:
                results.append((k, v))

        if value and results:
            for i in results:
                self.settings[i[0]] = value
            return
        elif results:
            if len(results) == 1:
                return results[0]
            else:
                return results
        else:
            return None

    def show_config(self):
        """
        Display current config.
        :return: Yaml object
        """
        return dump(inflate_dict(self.settings), default_flow_style=False)

    def get(self, header=None):
        """
        Get the value associated with header
        :param header: key to search
        :return: list of tuples
        """
        return self._find_header(header=header)

    def set(self, header, value):
        """
        Sets the value associated with the header
        :param header: key to search
        :param value: new value
        :return:
        """
        self._find_header(header=header, value=value)

    def save(self):
        """
        Save current settings to file.
        :return:
        """
        with open("./settings.yml", 'w') as _:
            dump(inflate_dict(self.settings), _, default_flow_style=False)