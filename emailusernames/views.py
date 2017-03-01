from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth import (login as auth_login, REDIRECT_FIELD_NAME,
    logout as auth_logout)
from django.contrib.auth.forms import AuthenticationForm

from .models import User

def get_user_or_404(slug):
    try:
        return User.get_from_slug(slug=slug)
    except User.DoesNotExist:
        raise Http404


def verify_email(request, slug, key):
    user = get_user_or_404(slug)
    if user.email_verified:
        messages.error(request, 'The email is already verified')
    else:
        if key == user.email_verification_code():
            user.activate()
            messages.success(request, 'Your email is successfully verified'
                ' and your account is activated.')
        else:
            messages.error(request, 'The activation link is incorrect.'
                'If you clicked the verification link on '
                'your email and get this message, contact Academy staff.')
    return HttpResponseRedirect(reverse('login'))


def send_email_verification_link(request, slug):
    user = get_user_or_404(slug)
    user.send_verification_email()
    messages.success(request, "Email sent. Click the link in it to verify.")
    return HttpResponseRedirect(reverse('login'))


def login(request, template_name='login.html', redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm):
    """
    Displays the login form and handles the login action.
    """
    context={}
    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        redirect_to = request.POST.get(redirect_field_name,
                        request.GET.get(redirect_field_name))
        if form.is_valid():
            auth_login(request, form.get_user())
            if request.user.email_verified:
                default_redirect = reverse('dashboard') if request.user.is_staff \
                                    else reverse('home')
                return HttpResponseRedirect(redirect_to or default_redirect)
            else:
                user = request.user
                auth_logout(request)
                resend_link = reverse('emailusernames:send-email-verification-link',
                    args=(user.slug,))
                messages.error(request, "You have not verified your email, yet."
                    " Please, check your inbox and click the verification link."
                    " <a href='%s'>Send verification email again.</a>"%resend_link)
        context[redirect_field_name] = redirect_to
    else:
        form = authentication_form(request)

    context['form'] = form
    return render(request, template_name, context)
