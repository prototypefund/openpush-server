import time
from io import BytesIO

import pycurl


def set_of(attr: str = None, data: dict = None):
    return set([d[attr] for d in data])


class CurlClient:
    def __init__(self, url, access_key, multi=None):
        self.buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(
            c.HTTPHEADER, ["X-Openpush-Key: " + access_key, "accept: text/event-stream"]
        )
        c.setopt(c.WRITEDATA, self.buffer)
        self.easy = c

        if multi:
            self.multi = multi
        else:
            self.multi = pycurl.CurlMulti()
        self.multi.add_handle(c)

    def get(self, timeout=0.1):
        """This calls get on the associated multi-handle. So it processes all
        transfers in parallel """
        start = time.time()
        readpopinter = self.buffer.tell()
        while True:
            ret, num_handles = self.multi.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break
        while num_handles:
            t = time.time()
            if t - start >= timeout:
                break
            ret = self.multi.select(timeout)
            if ret == -1:
                continue
            while True:
                ret, num_handles = self.multi.perform()
                if ret != pycurl.E_CALL_MULTI_PERFORM:
                    break
        self.buffer.seek(readpopinter)

    def get_finished(self):
        return self.multi.info_read()[1]

    def is_finished(self):
        return self.easy in self.get_finished()

    def shutdown(self):
        self.easy.close()
