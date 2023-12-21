import os
import time
import django

from django.utils import timezone

os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
django.setup()

from django.contrib.auth.models import User
from toima.models import Contact, ContactRequest, Message

def main():
    # Delete existing objects:
    for x in User.objects.all():
        x.delete()
    
    for x in Contact.objects.all():
        x.delete()

    for x in ContactRequest.objects.all():
        x.delete()
    
    for x in Message.objects.all():
        x.delete()

    # Create users:
    # All usernames and passwords are from here:
    # https://github.com/danielmiessler/SecLists/blob/master/Passwords/Common-Credentials/10-million-password-list-top-1000.txt

    # Superuser
    u0 = User.objects.create_superuser('admin', password='trustno1')
    u0.save()

    # Five normal users
    u1 = User.objects.create_user('superman', password='letmein')
    u1.save()

    u2 = User.objects.create_user('dragon', password='qwerty')
    u2.save()

    u3 = User.objects.create_user('angel', password='123456')
    u3.save()

    u4 = User.objects.create_user('thunder', password='whatever')
    u4.save()

    u5 = User.objects.create_user('falcon', password='qazwsx')
    u5.save()

    # ContactRequests and contacts
    ContactRequest(
        sender = u1, receiver=u3, msg="Hi! We met at the conference week ago. I was wearing a black hat and a pair of green trousers.").save()

    ContactRequest(
        sender = u0, receiver=u4,
        was_answered=timezone.now(), is_accepted=True,
        was_read=timezone.now()).save()
    Contact(owner=u4, contact=u0).save()
    Contact(owner=u0, contact=u4).save()

    ContactRequest(
        sender = u4, receiver=u3,
        was_answered=timezone.now(), is_accepted=True,
        was_read=timezone.now()).save()
    Contact(owner=u4, contact=u3).save()
    Contact(owner=u3, contact=u4).save()

    ContactRequest(
        sender = u3, receiver=u5,
        was_answered=timezone.now(), is_accepted=True,
        was_read=timezone.now()).save()
    Contact(owner=u5, contact=u3).save()
    Contact(owner=u3, contact=u5).save()

    ContactRequest(
        sender = u4, receiver=u5,
        was_answered=timezone.now(), is_accepted=True,
        was_read=timezone.now()).save()
    Contact(owner=u5, contact=u4).save()
    Contact(owner=u4, contact=u5).save()

    # Messages
    Message(
        sender=u3, receiver=u4, was_read=timezone.now(),
        msg="How are you?").save()
    time.sleep(0.005)
    Message(
        sender=u4, receiver=u3, was_read=timezone.now(),
        msg="I'm fine. How are you?").save()
    time.sleep(0.005)
    Message(
        sender=u3, receiver=u4, was_read=timezone.now(),
        msg="I'm fine too. What should we eat tomorrow?").save()
    time.sleep(0.005)
    Message(
        sender=u4, receiver=u3,
        msg="Maybe vegetable stew with rice?").save()
    time.sleep(0.005)
    Message(
        sender=u4, receiver=u3,
        msg="... or would you prefer potatoes?").save()

if __name__ == "__main__":
    main()