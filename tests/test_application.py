from utils import set_of


class TestApplication:
    def test_fetch_all(self, testapp):
        res = testapp.get(
            "/application", headers={"X-Openpush-Key": "aaaaAAAAbbbbBBBB0000111-C1"}
        )
        data = res.json
        assert len(data) == 2
        assert set_of("name", data) == {"app_c1_1", "app_c1_2"}

    def test_fetch_empty(self, testapp):
        res = testapp.get(
            "/application", headers={"X-Openpush-Key": "aaaaAAAAbbbbBBBB0000111-C2"}
        )
        data = res.json
        assert len(data) == 0

    def test_create(self, testapp):
        res = testapp.post_json(
            "/application",
            {"name": "New App"},
            headers={"X-Openpush-Key": "aaaaAAAAbbbbBBBB0000111-C1"},
        )
        assert res.status_int == 201
        data = res.json
        assert (
            data["routing_token"] != "aaaaAAAAbbbbBBBB0000111-A1"
            and data["routing_token"] != "aaaaAAAAbbbbBBBB0000111-A2"
        )
        assert len(data["routing_token"]) == 27
        res = testapp.get(
            "/application", headers={"X-Openpush-Key": "aaaaAAAAbbbbBBBB0000111-C1"}
        )
        data = res.json
        assert len(data) == 3
        assert set_of("name", data) == {"app_c1_1", "app_c1_2", "New App"}

    def test_delete(self, testapp):
        res = testapp.delete(
            "/application/2", headers={"X-Openpush-Key": "aaaaAAAAbbbbBBBB0000111-C1"}
        )
        assert res.status_int == 204
        res = testapp.get(
            "/application", headers={"X-Openpush-Key": "aaaaAAAAbbbbBBBB0000111-C2"}
        )
        data = res.json
        assert "app_c1_2" not in set_of("name", data)
