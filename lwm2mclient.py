import getopt
import sys
from lwm2mthon.client.client import Client

__author__ = 'jacko'


def usage():  # pragma: no cover
    print "lwm2mclient.py -d <device.json> -c <complete.json>"


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hd:c:", ["device=", "complete="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-d", "--device"):
            device = arg
        elif opt in ("-c", "--complete"):
            complete = arg
    client = Client(("127.0.0.1", 5685), device, complete)
    try:
        client.start()
    except KeyboardInterrupt:
        print "Server Shutdown"
        client.close()
        print "Exiting..."

if __name__ == "__main__":  # pragma: no cover
     main(sys.argv[1:])
