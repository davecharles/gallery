# Gallery
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

## Prerequisites
Download the [Google App Engine Python SDK](https://cloud.google.com/appengine/downloads) for your platform.
Install `app-engine-python` and `app-engine-python-extras.`

## Local Usage
Clone this repo and navigate to the `gallery/` directory.  Execute:

```
dev_appserver.py app.yaml
```

Navigate your browser to `http://localhost:8080` to view the Gallery application.

## Deploying to GCP

Make sure you have a project configured and are authorised with GCP.  Navigate to the `gallery/`
directory and execute:

```
gcloud app deploy app.yaml index.yaml
```

Navigate your browser to `https://your-app-id.appost.com` to view a hosted Gallery application.
