from MessageHeaders.msg_core import *


class CommandMessage(MultiPartMessage):
    header = b'COMMAND'

    def __init__(self):
        self.message = 'message'

    @property
    def msg(self):
        return [self.header, self.message.encode('utf-8')]

    @classmethod
    def from_msg(cls, msg):
        if len(msg) != 5 or msg[0] != cls.header:
            return None
        return cls(msg[1].decode('utf-8'))
