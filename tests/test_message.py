from orm import Message


# Want to test for:
# * No messages are ever lost
# * messages go to the correct client
# * client only connected once


class TestMessage:
    def test_send(self, testapp, db):
        # minimal fields set
        testapp.post_json(
            "/message",
            {"body": "Message1"},
            headers={"X-Openpush-Key": "aaaaAAAAbbbbBBBB0000111-A1"},
        )
        # everything set
        testapp.post_json(
            "/message",
            {"body": "Message2", "priority": "HIGH", "subject": "subject"},
            headers={"X-Openpush-Key": "aaaaAAAAbbbbBBBB0000111-A1"},
        )
        assert len(db.session.query(Message).all()) == 4
        # missing body
        res = testapp.post_json(
            "/message",
            {"priority": "HIGH", "subject": "subject"},
            expect_errors=True,
            headers={"X-Openpush-Key": "aaaaAAAAbbbbBBBB0000111-A1"},
        )
        assert res.status_int == 400
        assert len(db.session.query(Message).all()) == 4
