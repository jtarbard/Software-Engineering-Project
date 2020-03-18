from main.app import flask_app
import unittest


# Yoinked from www.youtube.com/watch?v=1aHNs1aEATg
class FlaskTestCase(unittest.TestCase):

    # Ensure flask was set up correctly
    def test_index(self):
        tester = flask_app.test_client(self)
        response = tester.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()