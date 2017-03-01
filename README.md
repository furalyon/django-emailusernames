===================
Django Entities App
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
    python manage.py migrate

Initial setup
=============

In your main ``urls.py`` add

    1) url(r'^emailusernames/', include('emailusernames.urls', namespace='emailusernames')),

    2) from emailusernames.views import login``

    3) url(r'^login$', login, {
        'template_name':'login.html'}, name='login'),

Templates
---------

    1) Customize the login template as you wish by creating a copy and just give the proper path above.

    2) Customize the ``email-base.html`` as you wish similarly by creating a copy to your templates base folder.

settings.py
-----------

    AUTH_USER_MODEL = 'emailusernames.User' #do not change
    STAFF_LOGIN_DEFAULT_REDIRECT = '/admin/' #change as you wish
    USER_LOGIN_DEFAULT_REDIRECT = '/' #change as you wish

    #Email sending setup as you normally do
    EMAIL_HOST = 'smtp.example.com'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = 'admin@example.com'
    EMAIL_HOST_PASSWORD = 'ghuihgiu9887967'
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = 'admin@example.com'
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

    EMAIL_VERIFICATION_NEEDED = True
    # Following settings are needed if you set EMAIL_VERIFICATION_NEEDED to True
    DOMAIN = 'example.com' #domain name of your site
    ORG_NAME = 'EXAMPLE' #name of the site organisation
    # change the following values for each site, the first time you setup
    EMAIL_VERIFY_ADDKEY_1 = 8979893431 #random 10 digit number
    EMAIL_VERIFY_ADDKEY_2 = 5445357861 #random 10 digit number
    EMAIL_VERIFY_MULTIPLYKEY_1 = 23 #random 2 digit number
    EMAIL_VERIFY_MULTIPLYKEY_2 = 67 #random 2 digit number

Signup Page
-----------
Create your own signup page. Just use

    from emailusernames.admin import UserCreationForm

as form for signup


Usage
=====

Once the setup is done, email address should now act as the username everywhere.