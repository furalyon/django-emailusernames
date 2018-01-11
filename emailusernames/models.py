from smtplib import SMTPRecipientsRefused
import random

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from django.conf import settings

from .utils import (decimal2base_n, base_n2decimal,
    send_email, render_template_as_string)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('Users must have an email address')

        email = UserManager.normalize_email(email)
        user = self.model(
            email=email, is_staff=False, is_active=True,
            is_superuser=False,
            last_login=now, date_joined=now, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        u = self.create_user(email, password, **extra_fields)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name=_('email address'),
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(
        _('First name'), max_length=255, blank=True)
    last_name = models.CharField(
        _('Last name'), max_length=255, blank=True)
    is_staff = models.BooleanField(
        _('Staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_privileged_staff = models.BooleanField(
        _('Privileged staff status'), default=False,
        help_text=_('Staff with special dashboard rights'))
    is_active = models.BooleanField(
        _('Active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'),
                                       default=timezone.now)

    email_verification_code = models.CharField(
        _('Email Verification Code'), max_length=16, blank=True)
    email_verified = models.BooleanField(_('Email Verified'), default = False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    SLUG_OFFSET = 121134

    # On Python 3: def __str__(self):
    def __str__(self):
        return self.get_short_name() or self.email

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def save(self, *args, **kwargs):
        new_user = not self.id
        super(User, self).save(*args, **kwargs)
        if not self.email_verified:
            try:
                verify = settings.EMAILUSERNAMES_VERIFY
            except AttributeError:
                # default False
                self.activate()
            else:
                if not verify or \
                    (self.is_staff or self.is_superuser):
                    self.activate()
                else:
                    if new_user:
                        self.send_verification_email()

    @property
    def slug(self):
        decimal_slug = self.pk + self.SLUG_OFFSET
        return str(decimal2base_n(decimal_slug))

    @classmethod
    def get_from_slug(cls, slug):
        decimal_slug = int(base_n2decimal(slug))
        return cls.objects.get(pk = decimal_slug - cls.SLUG_OFFSET)

    @staticmethod
    def get_random_hexkey():
        key = random.randint(100000000, 999999999)
        return str(decimal2base_n(key))

    def set_new_email_verification_code(self):
        self.email_verification_code = self.get_random_hexkey()
        self.save()
    
    def email_verification_link(self):
        return reverse('emailusernames:verify-email', kwargs = {
            'slug':self.slug,
            'key':self.email_verification_code,
            })

    def activate(self):
        self.email_verified = True
        self.save()
    activate.alters_data = True

    def send_verification_email(self):
        self.set_new_email_verification_code()
        base_url = settings.BASE_URL.rstrip('/')
        html_message = render_template_as_string(
            'emailusernames/verify-email.html',{
            'activation_url':base_url+self.email_verification_link(),
            'domain':base_url,
            })
        try:
            send_email('Email Verification',
                '', [self.email], html_message=html_message)
        except SMTPRecipientsRefused:
            self.delete()
            raise SMTPRecipientsRefused(_("Please enter a valid email address"))
