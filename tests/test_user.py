from utils import set_of


class TestUser:
    def test_fetch_all(self, testapp):
        testapp.authorization = ("Basic", ("User 1", "password1"))
        res = testapp.get("/user")
        data = res.json
        assert len(data) == 2
        assert set_of("name", data) == {"User 1", "User 2"}

    def test_fetch_one(self, testapp):
        testapp.authorization = ("Basic", ("User 1", "password1"))
        res = testapp.get("/user/1")
        data = res.json
        assert data["id"] == 1

    def test_update(self, testapp):
        testapp.authorization = ("Basic", ("User 1", "password1"))
        res = testapp.post_json("/user/1", {"name": "newname", "password": "newpass"})
        data = res.json
        assert data["name"] == "newname"
        testapp.authorization = ("Basic", ("newname", "newpass"))
        res = testapp.post_json("/user/1", {"name": "User 1", "password": "password1"})
        data = res.json
        assert data["name"] == "User 1"

    def test_delete(self, testapp):
        testapp.authorization = ("Basic", ("User 1", "password1"))
        res = testapp.delete("/user/2")
        assert res.status_int == 204
        res = testapp.get("/user/2", expect_errors=True)
        assert res.status_int == 404

    def test_create(self, testapp):
        testapp.authorization = ("Basic", ("User 1", "password1"))
        res = testapp.post_json("/user", {"name": "New User", "password": "newpass"})
        assert res.status_int == 201
        data = res.json
        res = testapp.get("/user/" + str(data["id"]))
        data = res.json
        assert data["name"] == "New User"
