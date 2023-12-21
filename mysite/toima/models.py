from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

class Contact(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='contact_set')
    contact = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='contacts')

    def new_messages_count(self):
        new_messages = self.contact.message_send_set.filter(
            Q(receiver=self.owner) & Q(was_read__isnull=True))
        return len(new_messages)

class ContactRequest(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='request_send_set')
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='request_recieved_set')
    was_sent = models.DateTimeField(auto_now_add=True)
    msg = models.TextField(blank=True)
    was_answered = models.DateTimeField(null=True)
    is_accepted = models.BooleanField(null=True)
    msg_answer = models.TextField(blank=True)
    was_read = models.DateTimeField(null=True)

class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='message_send_set')
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='message_recieved_set')
    was_sent = models.DateTimeField(auto_now_add=True)
    msg = models.TextField(blank=True)
    was_read = models.DateTimeField(null=True)
