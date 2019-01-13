from hydra.HydraMessenger.MessageHeaders.msg_core import *


class CommandMessage(MultiPartMessage):
    header = b'REPLY'

    def __init__(self, message='END'):
        self.message = message

    @property
    def msg(self):
        return [self.header, self.message.encode('utf-8')]

    @classmethod
    def from_msg(cls, msg):
        if msg[0] != cls.header:
            return None
        return cls(msg[1].decode('utf-8'))
