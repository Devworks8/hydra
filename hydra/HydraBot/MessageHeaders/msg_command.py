from hydra.HydraBot.MessageHeaders.msg_core import *


class CommandMessage(MultiPartMessage):
    header = b'COMMAND'

    def __init__(self):
        pass

    @property
    def msg(self):
        return [b'src', b'dest', b'cmd', b'work']

    @classmethod
    def from_msg(cls, msg):
        if msg[0] != cls.header:
            return None
        return cls(msg[1].decode('utf-8'))
