import zmq

from Utils.configure import CfgManager
from Utils.clireport import CLIReport


def main():
    """
    parser = ArgumentParser(description='Hydra Client')
    parser.add_argument('proxy',
                        help='Proxy server address')
    parser.add_argument('frontend_port',
                        help='Frontend proxy port for clients to connect to.')
    args = parser.parse_args()
    """

    try:
        settings = CfgManager()
        reporter = CLIReport(settings=settings)

    except:
        reporter.report('ERROR', 'Failed to parse settings.')

    frontend = "tcp://{}:{}".format(settings.get('service_proxy_host')[1],
                                    settings.get('service_proxy_port')[1])

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.LINGER, 0)

    reporter.report('INFO','Connecting to {}'.format(frontend))
    try:
        socket.connect(frontend)
        reporter.report('INFO', 'Connected.')

    except:
        reporter.report('ERROR',
                        'Failed to connect to tcp://{}:{}.'.format(settings.get('service_proxy_frontend_host')[1],
                                                                   settings.get('service_proxy_frontend_port')[1]))

    msgs = [b'1', b'2', b'3', b'4']
    while True:
        for msg in msgs:
            socket.send_multipart(msgs)
            poller = zmq.Poller()
            poller.register(socket, zmq.POLLIN)
            if poller.poll(10 * 1000):
                response = socket.recv_multipart()
                print(response)


if __name__ == "__main__":
    main()
