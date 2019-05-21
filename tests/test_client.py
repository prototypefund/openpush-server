from utils import set_of


class TestClient:
    def test_fetch_all(self, testapp):
        testapp.authorization = ("Basic", ("User 1", "password1"))
        res = testapp.get("/client")
        data = res.json
        assert len(data) == 2
        assert set_of("name", data) == {"client_u1_1", "client_u1_2"}

    def test_fetch_empty(self, testapp):
        testapp.authorization = ("Basic", ("User 2", "password2"))
        res = testapp.get("/client")
        data = res.json
        assert len(data) == 0

    def test_create(self, testapp):
        testapp.authorization = ("Basic", ("User 1", "password1"))
        res = testapp.post_json("/client", {"name": "New Client"})
        data = res.json
        assert res.status_int == 201
        assert (
            data["token"] != "aaaaAAAAbbbbBBBB0000111-C1"
            and data["token"] != "aaaaAAAAbbbbBBBB0000111-C2"
        )
        assert len(data["token"]) == 27
        res = testapp.get("/client")
        data = res.json
        assert len(data) == 3
        assert set_of("name", data) == {"client_u1_1", "client_u1_2", "New Client"}

    def test_delete(self, testapp):
        testapp.authorization = ("Basic", ("User 1", "password1"))
        res = testapp.delete("/client/2")
        assert res.status_int == 204
        res = testapp.get("/client")
        data = res.json
        assert "client_u1_2" not in set_of("name", data)

    def test_update(self, testapp):
        testapp.authorization = ("Basic", ("User 1", "password1"))
        res = testapp.put_json("/client/1", {"name": "New Name"})
        data = res.json
        assert data["name"] == "New Name"
        assert data["token"] == "aaaaAAAAbbbbBBBB0000111-C1"
