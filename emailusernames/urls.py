from django.urls import path
from .views import verify_email, send_email_verification_link, login
from django.conf import settings

app_name = 'emailusernames'

urlpatterns = [
    path('verify-email/<str:slug>/<str:key>',
        verify_email, name="verify-email"),
    path('send-email-verification-link/<str:slug>',
        send_email_verification_link,
        name='send-email-verification-link'),
    path('login', login, {
       'template_name':'login.html'}, name='login'),
]