===================
Django EmailUsernames App
===================


A simple django app to add values to ``models.ForeignKey`` fields on forms with a single name field (and may be an autopopulated slug field) on the fly ajaxically.


Pre-requisites
==============
    1) This was built for Python 3.x. But just change __str__ to __unicode__ in the models and you should be fine with python 2.7
    2) Django 1.8+


Installation
============

Download a copy of the emailusernames app folder in the repo and put it in your project folder.

Add ``emailusernames`` to your ``INSTALLED_APPS`` setting

    INSTALLED_APPS = (
        ...
        'emailusernames',
    )

Migrate database
----------------
NOTE: MIGRATION OF emailusernames HAS TO HAPPEN BEFORE admin

    python manage.py migrate


Initial setup
=============

In your main ``urls.py`` add

    path('user/', include('emailusernames.urls',
        namespace='emailusernames')),

Templates
---------

    1) Customize the login template as you wish by creating a copy and just give the proper path above.

    2) Customize the ``email-base.html`` as you wish similarly by creating a copy to your templates base folder.

settings.py
-----------

    AUTH_USER_MODEL = 'emailusernames.User' #do not change
    LOGIN_URL = '/user/login' #the 'user' value is same as in url include
    LOGIN_REDIRECT_URL = '/' #change as you wish

    # Email verification
    EMAILUSERNAMES_VERIFY = False # True if email verification is needed
    BASE_URL = 'http://<your-site.com>' # Needed to send absolute link to email

    # Email sending setup as you normally do
    EMAIL_HOST = 'smtp.example.com'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = 'admin@example.com'
    EMAIL_HOST_PASSWORD = 'ghuihgiu9887967'
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = 'admin@example.com'
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

    # Add 'emailusernames.context_processors.user_resources', to 
    # context_processors
    TEMPLATES = [
        {
            ....
            'OPTIONS': {
                ....
                'context_processors': [
                    ....
                    'emailusernames.context_processors.user_resources',
                ],
            },
        },
    ]


Signup Page
-----------
Create your own signup page. Just use

    from emailusernames.admin import UserCreationForm

as form for signup

Usage
=====

Once the setup is done, email address should now act as the username everywhere.
