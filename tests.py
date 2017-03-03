import unittest
from server import app
# import doctest


class MyAppIntegrationTestCase(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_homepage(self):
        result = self.client.get('/')
        self.assertIn('Click <a href="/login">here</a> to login.', result.data)

    def test_login_form(self):
        result = self.client.get('/login',
                                 data={'email': "j@gmail.com", 'password': "jl"},
                                 follow_redirects=True)
        self.assertIn("Location", result.data)
        self.assertNotIn('Click <a href="/login">here</a> to login.', result.data)




# class MyTest(unittest.TestCase):

#     def setUp(self):
#         self.client = server.app.test_client()
#         server.app.config['TESTING'] = True

#     def test_home(self):
#         result = self.client.get('/')
#         self.assertEqual(result.status_code, 200)

if __name__ == '__main__':
    unittest.main()
