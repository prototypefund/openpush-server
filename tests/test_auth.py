class TestAuth:
    def test_user_auth_success(self, testapp):
        testapp.authorization = ("Basic", ("User 1", "password1"))
        res = testapp.get("/user")
        assert res.status_int == 200

    def test_user_auth_fail(self, testapp):
        testapp.authorization = ("Basic", ("User 1", "password2"))
        res = testapp.get("/user", expect_errors=True)
        assert res.status_int == 401

    def test_user_noauth(self, testapp):
        res = testapp.get("/user", expect_errors=True)
        assert res.status_int == 401

    def test_client_auth_success(self, testapp):
        res = testapp.get(
            "/application", headers={"X-Openpush-Key": "aaaaAAAAbbbbBBBB0000111-C1"}
        )
        assert res.status_int == 200

    def test_client_auth_fail(self, testapp):
        res = testapp.get(
            "/application",
            expect_errors=True,
            headers={"X-Openpush-Key": "aaaaAAAAbbbbBBBBINVALID-XX"},
        )
        assert res.status_int == 401

    def test_client_noauth(self, testapp):
        res = testapp.get("/application", expect_errors=True)
        assert res.status_int == 401

    def test_message_noauth(self, testapp):
        res = testapp.post("/message", expect_errors=True)
        assert res.status_int == 400

    def test_version_noauth(self, testapp):
        res = testapp.get("/version")
        assert res.status_int == 200
