import getopt
import sys
from lwm2mthon.client.client import Client

__author__ = 'jacko'


def usage():  # pragma: no cover
    print "lwm2mclient.py -d <device.json>"


def main(argv):
    device = None
    try:
        opts, args = getopt.getopt(argv, "hd:", ["device="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-d", "--device"):
            device = arg

    client = Client(("127.0.0.1", 0), device)
    try:
        client.start()
    except KeyboardInterrupt:
        print "Server Shutdown"
        client.close()
        print "Exiting..."

if __name__ == "__main__":  # pragma: no cover
    main(sys.argv[1:])

