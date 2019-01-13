class MultiPartMessage(object):
    header = None

    @classmethod
    def recv(cls, socket):
        return cls.from_msg(socket.recv_multipart())

    @property
    def msg(self):
        return [b'src', b'dest', b'command', b'work']

    def send(self, socket, identity=None):
        msg = self.msg
        if identity:
            msg = [identity] + msg
            socket.send_multipart(msg)