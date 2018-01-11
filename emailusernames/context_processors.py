from django.conf import settings

def user_resources(request):
    return {
        'LOGIN_URL': settings.LOGIN_URL,
    }
