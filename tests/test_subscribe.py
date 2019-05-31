import json

import pycurl
import sseclient
from io import BytesIO
import time
import pytest

from orm import Message


# Want to test for:
# * No messages are ever lost
# * messages go to the correct client


class TestSubscribe:
    def test_receive(self, testserver, testapp, db):
        url = testserver.url + "/subscribe"
        c = CurlClient(url, "aaaaAAAAbbbbBBBB0000111-C1")
        # receiving stored messages
        c.get()
        client = sseclient.SSEClient(c.buffer)
        m1 = json.loads(next(client.events()).data)
        m2 = json.loads(next(client.events()).data)
        assert m1["body"] == "Body1"
        assert m2["body"] == "Body2"
        assert len(db.session.query(Message).all()) == 0

        # receiving new messages
        testapp.post_json(
            "/message",
            {"body": "Message1"},
            headers={"X-Openpush-Key": "aaaaAAAAbbbbBBBB0000111-A1"},
        )
        c.get()
        assert json.loads(next(client.events()).data)["body"] == "Message1"
        assert len(db.session.query(Message).all()) == 0
        # messages are stored after client disconnect
        client.close()
        c.shutdown()
        testapp.post_json(
            "/message",
            {"body": "Message1"},
            headers={"X-Openpush-Key": "aaaaAAAAbbbbBBBB0000111-A1"},
        )
        assert len(db.session.query(Message).all()) == 1

    def test_multiple_connect(self, testserver):
        """Test that if the same client connects again the first instance is
        disconnected """
        url = testserver.url + "/subscribe"
        multi = pycurl.CurlMulti()
        c = CurlClient(url, "aaaaAAAAbbbbBBBB0000111-C1", multi)
        c.get()
        c2 = CurlClient(url, "aaaaAAAAbbbbBBBB0000111-C1", multi)
        c2.get()
        assert c.is_finished()

    def test_different_clients(self, testserver, testapp):
        """Test connection by different clients"""
        testapp.post_json(
            "/message",
            {"body": "Message1"},
            headers={"X-Openpush-Key": "aaaaAAAAbbbbBBBB0000111-A1"},
        )
        url = testserver.url + "/subscribe"
        multi = pycurl.CurlMulti()
        c = CurlClient(url, "aaaaAAAAbbbbBBBB0000111-C1", multi)
        c2 = CurlClient(url, "aaaaAAAAbbbbBBBB0000111-C2", multi)
        c.get()
        assert not c.is_finished()
        client = sseclient.SSEClient(c.buffer)
        # client1 should have a message
        next(client.events())
        client2 = sseclient.SSEClient(c2.buffer)
        # and client2 shouldn't
        with pytest.raises(StopIteration):
            next(client2.events())


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

    def get(self, timeout=0.5):
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
            ret = self.multi.select(1.0)
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
        self.multi.close()
        self.easy.close()
