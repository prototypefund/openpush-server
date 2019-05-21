from utils import set_of


class TestUser:
    def test_fetch_all(self, testapp):
        testapp.authorization = ('Basic', ('User 1', 'password1'))
        res = testapp.get('/user')
        data = res.json
        assert len(data) == 2
        assert set_of('name', data) == {'User 1', 'User 2'}
