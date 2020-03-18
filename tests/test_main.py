from main.app import flask_app
import unittest


# Yoinked from www.youtube.com/watch?v=1aHNs1aEATg
class FlaskTestCase(unittest.TestCase):

    # Ensure flask was set up correctly and the website runs
    def test_index(self):
        tester = flask_app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Ensure the membership page loads correctly
    # Note: this is really primitive...
    # TODO: Find some way that extracts the title & content of a page. What is the criteria that defines a page loads correctly?
    def test_membership(self):
        tester = flask_app.test_client(self)
        response = tester.get('/info/memberships', content_type='html/text')
        print(response.data) # debug. learning what response data contains
        self.assertIn(b'Memberships', response.data)


if __name__ == '__main__':
    unittest.main()

