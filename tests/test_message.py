from orm import Message


class TestMessage:
    def test_send(self, testapp, db):
        # minimal fields set
        testapp.post_json(
            "/message", {"token": "aaaaAAAAbbbbBBBB0000111-A1", "data": {}}
        )
        # everything set
        testapp.post_json(
            "/message",
            {
                "token": "aaaaAAAAbbbbBBBB0000111-A1",
                "data": {"foo": "bar"},
                "priority": "HIGH",
                "collapse_key": "foobar",
                "time_to_live": 100,
            },
        )
        assert len(db.session.query(Message).all()) == 4
        # missing token
        res = testapp.post_json("/message", {"data": {}}, expect_errors=True)
        assert res.status_int == 400
        assert len(db.session.query(Message).all()) == 4
        # missing data
        res = testapp.post_json(
            "/message", {"token": "aaaaAAAAbbbbBBBB0000111-A1"}, expect_errors=True
        )
        assert res.status_int == 400
        assert len(db.session.query(Message).all()) == 4
