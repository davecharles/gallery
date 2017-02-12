"""Gallery.

Simple web application that allows a signed-in or anonymous user
to view images.

Signed-in users can upload images, add a description and set
whether it is public or private.  Signed-in users can see all
their own uploaded images and any public images uploaded by other
users.

The application was developed using Python 2.7.6 using the ``webapp2``
framework and is intended for deployment to Google App Engine.  Google
Cloud Datastore is used via the ``ndb`` client to store images and
their details.
"""
import os

from google.appengine.api import images
from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'templates')
    )
)


PAGE_SIZE = 20
IMAGE_SIZE = 256
DEFAULT_PAGE_TITLE = 'Gallery'


def gallery_key():
    """Datastore key for all gallery entries.

    All gallery entries are added under this key.
    """
    return ndb.Key('Gallery', 'All')


def make_template_values(request):
    """Make template values.

    Simple helper to create common values used to render
    application templates.

    :param Request request:  A google.appengine.ext.webapp.Request instance.
    :return: Dictionary.
    """
    user = users.get_current_user()
    values = {'request': request}
    if user:
        values['logged_in'] = True
        values['loginout_url'] = users.create_logout_url(request.uri)
        values['loginout_url_linktext'] = 'Logout ({})'.format(user)
    else:
        values['logged_in'] = False
        values['loginout_url'] = users.create_login_url(request.uri)
        values['loginout_url_linktext'] = 'Login'
    return values


class UploadedImage(ndb.Model):
    """Models a user's uploaded image."""
    owner = ndb.UserProperty(required=True)
    image = ndb.BlobProperty()
    description = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    public = ndb.BooleanProperty()


class Home(webapp2.RequestHandler):
    """Home page handler.

    The Home page displays all uploaded images that are marked as public.
    Additionally if the user is signed in then their private images are
    also displayed.
    """
    def get(self):
        # Get all 'public' images
        public_images_query = UploadedImage.query(ancestor=gallery_key())
        public_images_query = public_images_query.filter(
            UploadedImage.public == True)
        public_images = public_images_query.fetch(PAGE_SIZE)

        current_user = users.get_current_user()
        if current_user:
            # User is signed in so get their private images
            private_images_query = UploadedImage.query(
                ancestor=gallery_key()).filter(
                UploadedImage.owner == current_user)
            private_images_query = private_images_query.filter(
                UploadedImage.public == False)
            private_images = private_images_query.order(
                -UploadedImage.date).fetch(PAGE_SIZE)
        else:
            private_images = []

        template_values = make_template_values(self.request)
        template_values['page_title'] = '{} - {}'.format(
            DEFAULT_PAGE_TITLE, 'Home')
        template_values['public_images'] = public_images
        template_values['private_images'] = private_images
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class Manage(webapp2.RequestHandler):
    """Manage Images page handler.

    The Manage Images page allows a signed-in user to view all
    their images and upload new ones.
    """
    def get(self):
        current_user = users.get_current_user()

        # Get all user's images
        user_images_query = UploadedImage.query(
            ancestor=gallery_key()).filter(
            UploadedImage.owner == current_user
        )
        user_images = user_images_query.order(
            -UploadedImage.date).fetch(PAGE_SIZE)
        template_values = make_template_values(self.request)
        template_values['page_title'] = '{} - {}'.format(
            DEFAULT_PAGE_TITLE, 'Manage Images')
        template_values['user_images'] = user_images
        template = JINJA_ENVIRONMENT.get_template('manage.html')
        self.response.write(template.render(template_values))


class About(webapp2.RequestHandler):
    """About page handler."""
    def get(self):
        template_values = make_template_values(self.request)
        template_values['page_title'] = '{} - {}'.format(
            DEFAULT_PAGE_TITLE, 'About')
        template = JINJA_ENVIRONMENT.get_template('about.html')
        self.response.write(template.render(template_values))


class Images(webapp2.RequestHandler):
    """Image Handler.

    Handler used to dynamically serve images from the /img path.
    """
    def get(self):
        img_key = ndb.Key(urlsafe=self.request.get('img_id'))
        uploaded_image = img_key.get()
        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(uploaded_image.image)


class Upload(webapp2.RequestHandler):
    """Upload Handler.

    Handler for image upload gesture.
    """
    def post(self):
        current_user = users.get_current_user()
        if current_user is None:
            # Belt and braces here - UI should disallow
            webapp2.abort(401)

        selected_image = self.request.get('img')
        if selected_image is None:
            # Belt and braces here - UI should disallow
            webapp2.abort(400)

        img = UploadedImage(parent=gallery_key())
        img.owner = users.get_current_user()
        img.image = images.resize(
            self.request.get('img'), IMAGE_SIZE, IMAGE_SIZE)
        img.description = self.request.get('description')
        img.public = self.request.get('public') == 'on'
        img.put()
        self.redirect('/manage')


routes = [
    ('/', Home),
    ('/manage', Manage),
    ('/about', About),
    ('/img', Images),
    ('/upload', Upload), ]


config = {}


app = webapp2.WSGIApplication(
    routes=routes,
    debug=True,
    config=config)


def main():
    app.run()


if __name__ == "__main__":
    main()
