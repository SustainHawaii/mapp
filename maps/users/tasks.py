from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template import loader
from maps.users.models import User
import hashlib, datetime, random


@shared_task()
def send_email_confirmation(site, user_id):
    site = ''.join(site)
    user = User.objects.get(id=user_id)

    user.is_active = False

    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
    activation_key = hashlib.sha1(salt + user.email).hexdigest()

    user.key_expires = datetime.datetime.today() + datetime.timedelta(2)
    user.activation_key = activation_key

    user.save()

    c = {'site': site, 'key': activation_key}
    from_email = settings.EMAIL_HOST_USER
    subject = loader.render_to_string('email/registration_subject.txt', c)
    subject = ''.join(subject.splitlines())
    email = loader.render_to_string('email/registration.html', c)

    send_mail(subject, email, from_email, [user.email], html_message=email)


@shared_task()
def send_email_recovery(site, user):
    site = ''.join(site)

    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
    activation_key = hashlib.sha1(salt + user.email).hexdigest()

    user.key_expires = datetime.datetime.today() + datetime.timedelta(2)
    user.activation_key = activation_key

    user.save()

    c = {'site': site, 'key': activation_key}
    from_email = settings.EMAIL_HOST_USER
    subject = loader.render_to_string('email/recovery_subject.txt', c)
    subject = ''.join(subject.splitlines())
    email = loader.render_to_string('email/recovery.html', c)

    send_mail(subject, email, from_email, [user.email], html_message=email)
