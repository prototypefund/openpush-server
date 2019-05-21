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
