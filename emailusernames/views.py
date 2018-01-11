from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import (login as auth_login, REDIRECT_FIELD_NAME,
    logout as auth_logout, authenticate as auth_authenticate)
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.conf import settings

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
        if key == user.email_verification_code:
            user.activate()
            messages.success(request, 'Your email is successfully verified'
                ' and your account is activated.')
        else:
            messages.error(request, 'The activation link is incorrect.'
                'If you clicked the verification link on '
                'your email and get this message, contact Academy staff.')
    return HttpResponseRedirect(settings.LOGIN_URL)


def send_email_verification_link(request, slug):
    user = get_user_or_404(slug)
    user.send_verification_email()
    messages.success(request, "Email sent. Click the link in it to verify.")
    return HttpResponseRedirect(settings.LOGIN_URL)


def login(request, template_name='login.html',
        redirect_field_name=REDIRECT_FIELD_NAME,
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
                return HttpResponseRedirect(redirect_to or settings.LOGIN_REDIRECT_URL)
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
        context['next'] = request.GET.get(redirect_field_name)

    context['form'] = form
    return render(request, template_name, context)


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation",
        widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email",)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            msg = "Passwords don't match"
            raise forms.ValidationError("Password mismatch")
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


def register(request):
    context={}
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
            except Exception as e:
                messages.error(request,'{}'.format(e))
            else:
                if email_verified:
                    email = request.POST['email']
                    password = request.POST['password1']
                    user = auth_authenticate(username = email,
                        password=password)
                    auth_login(request, user)
                    return HttpResponseRedirect(reverse('home'))
                else:
                    messages.success(request,
                        'Account created! Verify Email ID by '
                        'clicking the link in the email sent to your inbox')
                    return HttpResponseRedirect(settings.LOGIN_URL)
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {
        'form':form,
        })

