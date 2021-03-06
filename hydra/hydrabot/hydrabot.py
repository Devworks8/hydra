from multiprocessing import Process, Queue
from random import randint
import os
from time import sleep
import signal
import zmq

from Utils.configure import CfgManager
from Utils.clireport import CLIReport
from MessageHeaders.msg_command import CommandMessage
from Shell.shell import CLIShell
from HPlayer.hplayer import Player


class HydraBot(Process):
    def __init__(self, reporter=None, settings=None, player=None, host=None, port=None):
        super().__init__()
        self.reporter = reporter
        self.settings = settings
        self.player = player
        self.command_message = CommandMessage()
        self.identity = "%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000))
        self.host = self.settings.get('service_proxy_host')[1]
        self.port = self.settings.get('service_proxy_port')[1]
        self.msgs = Queue()

    def validate_message(self, msg):
        headers = [b'COMMAND', b'REPLY']
        commands = [b'PLAY']

        if msg[0] in headers and len(msg) > 1:
            if msg[1] in commands:
                return True
            else:
                return False
        else:
            return False

    def send_cmd(self, msg, opt=None):
        options = {'player': 'self.player.play()'}

        if self.validate_message(msg=msg):
            self.msgs.put(msg)
            if opt in options:
                eval(options[opt])
        else:
            print('invalid')

    def run(self):
        try:
            settings = CfgManager()
            reporter = CLIReport(settings=settings)

        except Exception as err:
            reporter.report('ERROR', 'Failed to parse settings.\n[{e}'.format(e=err))

        frontend = "tcp://{}:{}".format(settings.get('service_proxy_host')[1],
                                        settings.get('service_proxy_port')[1])

        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.setsockopt(zmq.LINGER, 0)

        reporter.report('INFO','Connecting to {}'.format(frontend))
        try:
            socket.connect(frontend)
            reporter.report('INFO', 'Connected.')

        except Exception as err:
            reporter.report('ERROR',
                            'Failed to connect to tcp://{host}:{port}'
                            '\n[{e}'.format(host=settings.get('service_proxy_frontend_host')[1],
                                            port=settings.get('service_proxy_frontend_port')[1],
                                            e=err))

        while True:
            if not self.msgs.empty():
                socket.send_multipart(self.msgs.get())
                poller = zmq.Poller()
                poller.register(socket, zmq.POLLIN)
                if poller.poll(10 * 1000):
                    response = socket.recv_multipart()
                    print(response)


processes = []


def signal_handler(_signum, _frame):
    for process in processes:
        if process.is_alive():
            os.kill(process.pid, signal.SIGKILL)

    for process in processes:
        process.join()


def main():
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    """
        parser = ArgumentParser(description='Hydra Client')
        parser.add_argument('proxy',
                            help='Proxy server address')
        parser.add_argument('frontend_port',
                            help='Frontend proxy port for clients to connect to.')
        args = parser.parse_args()
        """

    # Load settings
    settings = CfgManager()

    # Load the reporter
    reporter = CLIReport(settings=settings)

    # Load the player
    player_proc = Player()
    processes.append(player_proc)

    # Start the Client
    client_proc = HydraBot(reporter=reporter, settings=settings, player=player_proc)
    client_proc.start()
    reporter.report('INFO', 'Client started.')
    processes.append(client_proc)

    sleep(1)
    # Start the shell
    CLIShell(bot=client_proc, settings=settings).cmdloop()


if __name__ == "__main__":
    main()
