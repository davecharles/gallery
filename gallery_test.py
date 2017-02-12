from google.appengine.ext import ndb
from google.appengine.ext import testbed
from google.appengine.api import users


try:
    import mock
except ImportError:
    from unittest import mock

import unittest
import webapp2

import gallery


class TestHandlers(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        # Clear ndb's in-context cache between tests.
        ndb.get_context().clear_cache()
        self.testbed.init_user_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def login_user(self, email='user@example.com', id='123', is_admin=False):
        self.testbed.setup_env(
            user_email=email,
            user_id=id,
            user_is_admin='1' if is_admin else '0',
            overwrite=True)

    def test_gallery_key(self):
        key = gallery.gallery_key()
        assert isinstance(key, ndb.Key)
        assert key == ndb.Key('Gallery', 'All')

    def test_make_template_values_logged_out(self):
        mock_request = mock.Mock()
        mock_request.uri = 'uri'
        values = gallery.make_template_values(mock_request)
        assert not values['logged_in']
        url = users.create_login_url(mock_request.uri)
        assert values['loginout_url'] == url
        assert values['loginout_url_linktext'] == 'Login'

    def test_make_template_values_logged_in(self):
        self.login_user()
        mock_request = mock.Mock()
        mock_request.uri = 'uri'
        values = gallery.make_template_values(mock_request)
        assert values['logged_in']
        url = users.create_logout_url(mock_request.uri)
        assert values['loginout_url'] == url
        assert values['loginout_url_linktext'] == 'Logout (user@example.com)'

    def test_home(self):
        request = webapp2.Request.blank('/')
        response = request.get_response(gallery.app)
        self.assertEqual(response.status_int, 200)

        # Check we have at least a title and navigation
        assert '<title>Gallery - Home</title>' in response.body
        assert '<a href="/">Home</a>' in response.body
        assert '<a href="/manage">Manage Images</a>' in response.body
        assert '<a href="/about">About</a>' in response.body

    def test_manage(self):
        request = webapp2.Request.blank('/manage')
        response = request.get_response(gallery.app)
        self.assertEqual(response.status_int, 200)
        assert 'You must be logged in to manage your images' in response.body

    def test_manage_logged_in(self):
        self.login_user()
        request = webapp2.Request.blank('/manage')
        response = request.get_response(gallery.app)
        self.assertEqual(response.status_int, 200)
        assert 'Load an Image...' in response.body

    def test_about(self):
        request = webapp2.Request.blank('/about')
        response = request.get_response(gallery.app)
        self.assertEqual(response.status_int, 200)
        assert 'Gallery is a simple web application' in response.body

    def test_upload_logged_out(self):
        request = webapp2.Request.blank('/upload')
        request.method = 'POST'
        response = request.get_response(gallery.app)
        self.assertEqual(response.status_int, 401)

    def test_upload_no_img(self):
        self.login_user()
        request = webapp2.Request.blank('/upload')
        request.method = 'POST'
        request.POST['img'] = None
        response = request.get_response(gallery.app)
        self.assertEqual(response.status_int, 400)


if __name__ == '__main__':
    unittest.main()