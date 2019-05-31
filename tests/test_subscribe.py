import json

import pycurl
import sseclient
from io import BytesIO
import time

from orm import Message


# Want to test for:
# * No messages are ever lost
# * messages go to the correct client
# * client only connected once


class TestSubscribe:
    def test_receive_stored(self, testserver, db):
        url = testserver.url + "/subscribe"
        c = CurlClient(url, "aaaaAAAAbbbbBBBB0000111-C1")
        c.get(timeout=0.1)
        client = sseclient.SSEClient(c.buffer)
        m1 = json.loads(next(client.events()).data)
        m2 = json.loads(next(client.events()).data)
        client.close()
        assert m1["body"] == "Body1"
        assert m2["body"] == "Body2"
        assert len(db.session.query(Message).all()) == 0
        c.shutdown()


class CurlClient:
    def __init__(self, url, access_key):
        self.buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(
            c.HTTPHEADER, ["X-Openpush-Key: " + access_key, "accept: text/event-stream"]
        )
        c.setopt(c.WRITEDATA, self.buffer)
        self.easy = c

        self.multi = pycurl.CurlMulti()
        self.multi.add_handle(c)

    def get(self, timeout=1.0):
        start = time.time()
        while True:
            ret, num_handles = self.multi.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break
        while num_handles:
            t = time.time()
            if t - start >= timeout:
                break
            ret = self.multi.select(1.0)
            if ret == -1:
                continue
            while True:
                ret, num_handles = self.multi.perform()
                if ret != pycurl.E_CALL_MULTI_PERFORM:
                    break
        self.buffer.seek(0)

    def shutdown(self):
        self.multi.close()
        self.easy.close()
