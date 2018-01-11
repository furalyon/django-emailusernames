from django.template import loader
from django.core.mail import EmailMessage
from django.conf import settings
import string
CHARS = string.digits+string.ascii_lowercase+string.ascii_uppercase
BASE = len(CHARS)

def decimal2base_n(n):
    if n >= BASE:
        return decimal2base_n(n // BASE) + CHARS[n % BASE]
    else:
        return CHARS[n]

def base_n2decimal(n):
    if len(n) > 1:
        return base_n2decimal(n[:-1]) * BASE + CHARS.index(n[-1])
    else:
        return CHARS.index(n[0])

def render_template_as_string(template_name, data_dict):
    t = loader.get_template(template_name)
    c = data_dict
    return t.render(c)

def send_email(subject, message, recipients, html_message='',
    sender=settings.DEFAULT_FROM_EMAIL, bcc_admin = False, bcc_list = []):

    subject = "%s - %s"%(settings.ORG_NAME, subject)
    if settings.DEBUG:
        print(message, html_message)
    bcc = [settings.CONTACT_EMAIL] if bcc_admin else []
    message = html_message or message
    email = EmailMessage(subject, message, sender, recipients, bcc+bcc_list)
    if html_message:
        email.content_subtype='html'
    email.send()
