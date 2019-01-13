class HydraMessageWorker(Process):
    def __init__(self, server=None, backend_port=None):
        super().__init__()
        self.settings = CfgManager()
        self.command_message = CommandMessage()
        self.identity = "%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000))
        self.backend_host = self.settings.get('service_proxy_backend_host')[1]
        self.backend_port = self.settings.get('service_proxy_backend_port')[1]
        self.crypto = self.settings.get('service_messenger_crypto')[1]

    def run(self):
        context = zmq.Context()
        worker = context.socket(zmq.REP)

        # setup crypto
        if self.crypto:
            keymonkey = KeyMonkey("HydraMessenger")
            worker = keymonkey.setupClient(worker, "tcp://{host}:{port}".format(host=self.backend_host,
                                                                                port=self.backend_port),
                                           "HydraProxyBackend")

        worker.connect("tcp://{host}:{port}".format(host=self.backend_host, port=self.backend_port))

        while True:
            message = worker.recv_multipart()
            worker.send_multipart(message)
            print("Worker %s sending results" % self.identity)
            print(message)