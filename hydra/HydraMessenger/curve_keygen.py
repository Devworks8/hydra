"""
	Modeled after ssh-keygen.
"""

import os, sys
import shutil
import zmq.auth
import argparse


class KeyGenerator(object):
    def __init__(self, myid="id_curve", dest=None):
        self.myid = myid
        if dest == None:
            self.curvedir = os.path.expanduser("~") + "/.curve"
        else:
            self.curvedir = dest
        self.public_key = self.curvedir + "/%s.key" % self.myid
        self.private_key = self.curvedir + "/%s.key_secret" % self.myid

    def generate(self):

        bogus = False
        for key in [self.public_key, self.private_key]:
            if os.path.exists(key):
                print("%s already exists. Aborting." % key)
                bogus = True
                break
        if bogus:
            sys.exit(1)

        if not os.path.exists(self.curvedir):
            os.mkdir(self.curvedir)
        os.chmod(self.curvedir, 0o700)

        # create new keys in certificates dir
        server_public_file, server_secret_file = zmq.auth.create_certificates(self.curvedir, self.myid)
        os.chmod(self.public_key, 0o600)
        os.chmod(self.private_key, 0o600)
        print("Created %s." % self.public_key)
        print("Created %s." % self.private_key)


if __name__ == '__main__':
    if zmq.zmq_version_info() < (4, 0):
        raise RuntimeError(
            "Security is not supported in libzmq version < 4.0. libzmq version {0}".format(zmq.zmq_version()))
    myid = "id_curve"
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="id_curve")
    parser.add_argument("-d", "--destination", type=str, help="specify output directory for keys", default=None)
    args = parser.parse_args()
    kg = KeyGenerator(args.name, dest=args.destination)
    kg.generate()
