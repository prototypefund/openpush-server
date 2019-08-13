import json
import threading
import time

import pycurl
import pytest
import sseclient
from utils import CurlClient

from orm import Message


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
        c2.shutdown()

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
        c.shutdown()
        c2.shutdown()

    def test_concurrent_receive(self, testserver, testapp, db):
        # Let's send lot's of messages while two clients reconnect concurrently
        # and make sure every message is delivered only once to either client.
        url = testserver.url + "/subscribe"
        c = CurlClient(url, "aaaaAAAAbbbbBBBB0000111-C1")
        # sc2 = CurlClient(url, "aaaaAAAAbbbbBBBB0000111-C1")

        class ReconnectingCurlClient(threading.Thread):
            def __init__(self, curl):
                threading.Thread.__init__(self)
                self.c = curl
                self.stop = threading.Event()

            def run(self):
                while not self.stop.is_set():
                    self.c.get()
                    if self.c.is_finished:
                        self.c.restart()
                    time.sleep(1)

        # t1 = ReconnectingCurlClient(c)
        # t2 = ReconnectingCurlClient(c2)
        # t1.start()
        # t2.start()
        c.get()
        for i in range(50):
            testapp.post_json(
                "/message",
                {"body": "Message" + str(i)},
                headers={"X-Openpush-Key": "aaaaAAAAbbbbBBBB0000111-A1"},
            )
            # time.sleep(0.005)

        # time.sleep(3)
        # t1.stop.set()
        # t2.stop.set()
        # c.get(3)
        assert len(db.session.query(Message).all()) == 0
