from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.urlresolvers import reverse
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
    is_active = models.BooleanField(
        _('Active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'),
                                       default=timezone.now)

    email_verified = models.BooleanField(_('Email Verified'), default = False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    SLUG_OFFSET = 121134

    # On Python 2: def __unicode__(self):
    def __str__(self):
        return self.get_short_name() or self.email

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def save(self, *args, **kwargs):
        send_email = not self.id
        super(User, self).save(*args, **kwargs)
        if settings.EMAIL_VERIFICATION_NEEDED:
            if not self.email_verified:
                if self.is_staff or self.is_superuser:
                    self.activate()
                else:
                    if send_email:
                        self.send_verification_email()
        else:
            self.activate()

    @property
    def slug(self):
        decimal_slug = self.pk + self.SLUG_OFFSET
        return str(decimal2base_n(decimal_slug))

    @classmethod
    def get_from_slug(cls, slug):
        decimal_slug = int(base_n2decimal(slug))
        return cls.objects.get(pk = decimal_slug - cls.SLUG_OFFSET)

    def hexkey_from_add_multiply_keys(self, addkey, multiplykey):
        key = addkey + self.pk * multiplykey
        return str(decimal2base_n(key))

    def email_verification_code(self):
        try:
            hexkey1 = self.hexkey_from_add_multiply_keys(
                settings.EMAIL_VERIFY_ADDKEY_1,
                settings.EMAIL_VERIFY_MULTIPLYKEY_1
                )
            hexkey2 = self.hexkey_from_add_multiply_keys(
                settings.EMAIL_VERIFY_ADDKEY_2,
                settings.EMAIL_VERIFY_MULTIPLYKEY_2
                )
        except:
            hexkey1 = self.hexkey_from_add_multiply_keys(
                5345645353,
                34
                )
            hexkey2 = self.hexkey_from_add_multiply_keys(
                3436464765,
                41
                )
        return "ac-{}-{}".format(hexkey1, hexkey2)
    
    def email_verification_link(self):
        return reverse('emailusernames:verify-email', kwargs = {
            'slug':self.slug,
            'key':self.email_verification_code(),
            })

    def activate(self):
        self.email_verified = True
        self.save()
    activate.alters_data = True

    def send_verification_email(self):
        html_message = render_template_as_string(
            'emailusernames/verify-email.html',{
            'activation_url':settings.DOMAIN+self.email_verification_link(),
            'domain':settings.DOMAIN,
            })
        send_email('Email Verification',
            '', [self.email], html_message=html_message)
