class TestAuth:
    def test_user_auth_success(self, testapp):
        testapp.authorization = ('Basic', ('User 1', 'password1'))
        res = testapp.get('/user')
        assert res.status_int == 200

    def test_user_auth_fail(self, testapp):
        testapp.authorization = ('Basic', ('User 1', 'password2'))
        res = testapp.get('/user', expect_errors=True)
        assert res.status_int == 401

    def test_user_noauth(self, testapp):
        res = testapp.get('/user', expect_errors=True)
        assert res.status_int == 401
