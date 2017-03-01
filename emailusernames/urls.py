from django.conf.urls import url
from .views import verify_email, send_email_verification_link, login

urlpatterns = [
    url(r'^verify-email/(?P<slug>\w+)/(?P<key>[-\w]+)$',
        verify_email, name="verify-email"),
    url(r'^send-email-verification-link/(?P<slug>\w+)$',
        send_email_verification_link,
        name='send-email-verification-link'),
]