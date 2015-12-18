from lwm2mthon.client.client import Client

__author__ = 'jacko'

if __name__ == "__main__":  # pragma: no cover
    client = Client(("127.0.0.1", 5685))
    try:
        client.start()
    except KeyboardInterrupt:
        print "Server Shutdown"
        client.close()
        print "Exiting..."
