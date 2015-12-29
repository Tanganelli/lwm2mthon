import logging
import threading
import time
from coapthon import defines
from coapthon.layers.observelayer import ObserveLayer

logger = logging.getLogger(__name__)


class ObserveItem(object):
    def __init__(self, timestamp, non_counter, allowed, transaction):
        self.timestamp = timestamp
        self.non_counter = non_counter
        self.allowed = allowed
        self.transaction = transaction


class LWM2MObserveLayer(ObserveLayer):
    def __init__(self, notify_method, stopped, root):
        super(LWM2MObserveLayer, self).__init__()
        self.notify_method = notify_method
        self.stopped = stopped
        self.root = root

        self.notify_task = threading.Thread(target=self.periodic_notification)
        self.notify_task.setDaemon(True)
        self.notify_task.start()

    def periodic_notification(self):
        sleep_time = 60
        while not self.stopped.isSet():
            logger.debug("Periodic Notification")
            self.stopped.wait(timeout=sleep_time)
            try:
                pmin = self.root["/1/1/2"].get_value()
            except KeyError:
                pmin = 20
            try:
                pmax = self.root["/1/1/3"].get_value()
            except KeyError:
                pmax = 60
            sleep_time = pmax
            observers = []
            now = time.time()
            for key in self._relations.keys():
                timestamp = self._relations[key].timestamp
                if timestamp is None or now > timestamp + pmin:
                    if self._relations[key].non_counter > defines.MAX_NON_NOTIFICATIONS \
                            or self._relations[key].transaction.request.type == defines.Types["CON"]:
                        self._relations[key].transaction.response.type = defines.Types["CON"]
                        self._relations[key].non_counter = 0
                    elif self._relations[key].transaction.request.type == defines.Types["NON"]:
                        self._relations[key].non_counter += 1
                        self._relations[key].transaction.response.type = defines.Types["NON"]
                    self._relations[key].transaction.resource.observe_count += 1
                    del self._relations[key].transaction.response.mid
                    del self._relations[key].transaction.response.token
                    observers.append(self._relations[key].transaction)

                else:
                    dif = timestamp + pmax - now
                    if dif < sleep_time:
                        sleep_time = dif
            self.notify_method(observers)

