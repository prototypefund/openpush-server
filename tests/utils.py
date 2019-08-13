import time
from io import BytesIO

import pycurl


def set_of(attr: str = None, data: dict = None):
    return set([d[attr] for d in data])


class CurlClient:
    def __init__(self, url, access_key, multi=None):
        self.buffer = BytesIO()
        self.url = url
        self.access_key = access_key
        self.easy = pycurl.Curl()
        if multi:
            self.multi = multi
        else:
            self.multi = pycurl.CurlMulti()
        self.curl_init()

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

    def curl_init(self):
        self.easy.reset()
        self.easy.setopt(self.easy.URL, self.url)
        self.easy.setopt(
            self.easy.HTTPHEADER,
            ["X-Openpush-Key: " + self.access_key, "accept: text/event-stream"],
        )
        self.easy.setopt(self.easy.WRITEDATA, self.buffer)
        self.multi.add_handle(self.easy)

    def restart(self):
        self.multi.remove_handle(self.easy)
        self.curl_init()

    def get_finished(self):
        return self.multi.info_read()[1]

    def is_finished(self):
        return self.easy in self.get_finished()

    def shutdown(self):
        self.easy.close()
