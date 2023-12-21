import sqlite3

from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# FLAW 1 Step 1: uncomment the following import statement
# from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .models import ContactRequest, Contact, Message


@login_required
def home(request):
    user = User.objects.get(username = request.user)
    cr_rec = user.request_recieved_set.filter(was_answered__isnull=True).order_by("-was_sent")
    cr_ans = user.request_send_set.filter(
        Q(was_answered__isnull=False) &
        Q(was_read__isnull=True)
    ).order_by("-was_answered")
    contacts = user.contact_set.all().order_by("contact__username")
    context = {
        'user': user,
        'cr_rec': cr_rec,
        'cr_ans': cr_ans,
        'contacts': contacts
    }

    return render(request, 'toima/home.html', context)

# FLAW 1 Step 2: replace the @login_required with
# @staff_member_required(login_url='/login/')
@login_required
def administration(request):
    user = User.objects.get(username = request.user)
    users = User.objects.all()
    context = {'user': user, 'users': users}
    
    return render(request, 'toima/administration.html', context)

# FLAW 1 Step 3: replace the @login_required with
# @staff_member_required(login_url='/login/')
@login_required
def administrationState(request, user_id):
    user = User.objects.get(pk = user_id)
    user.is_active = not user.is_active
    user.save()
    return HttpResponseRedirect(reverse("toima:administration"))

@login_required
def sendRequest(request):
    sender = request.user
    msg = request.POST.get("message")

    try:
        receiver = User.objects.get(
            username=request.POST.get("username"))
    except ObjectDoesNotExist:
        # The typed username does not belong to any real user
        return HttpResponseRedirect(reverse("toima:home"))
    
    if sender == receiver:
        # Receiver is the sender
        return HttpResponseRedirect(reverse("toima:home"))
    elif len(
        sender.contact_set.filter(contact=receiver.pk)
        ) > 0:
        # Receiver is already sender's contact
        return HttpResponseRedirect(reverse("toima:home"))
    elif len(sender.request_send_set.filter(
            Q(receiver=receiver.pk) & Q(was_answered__isnull=True)
        )) > 0:
        # Sender has already sended a request to the receiver and the receiver has not yet answered.
        return HttpResponseRedirect(reverse("toima:home"))
    elif len(receiver.request_send_set.filter(
            Q(receiver=sender.pk) & Q(was_answered__isnull=True)
        )) > 0:
        # Receiver has already sended a request to the sender and the sender has not yet answered.
        return HttpResponseRedirect(reverse("toima:home"))

    ContactRequest.objects.create(
        sender=sender, receiver=receiver, msg=msg).save()

    return HttpResponseRedirect(reverse("toima:home"))

# FLAW 3 Step 1: comment out the following line
@csrf_exempt
@login_required
def answerRequest(request, cr_id):
    cr = ContactRequest.objects.get(pk=cr_id)

    if cr.receiver != request.user:
        # Verify that the request does not belong to anybody else
        return HttpResponseRedirect(reverse("toima:home"))

    if cr.was_answered is not None:
        # Verify that there is no answer already
        return HttpResponseRedirect(reverse("toima:home"))
    
    cr.was_answered = timezone.now()

    is_accepted = False
    if 'accept' in request.POST:
        is_accepted = True
        Contact.objects.create(
            owner=cr.sender, contact=cr.receiver).save()
        if not cr.sender in cr.receiver.contact_set.all():
            Contact.objects.create(
                owner=cr.receiver, contact=cr.sender).save()

    cr.is_accepted = is_accepted
    cr.msg_answer = request.POST.get("msg_answer")
    cr.save()
    return HttpResponseRedirect(reverse("toima:home"))

@login_required
def readAnswer(request, cr_id):
    cr = ContactRequest.objects.get(pk=cr_id)

    if cr.sender != request.user:
        # Verify that the request does not belong to anybody else
        return HttpResponseRedirect(reverse("toima:home"))
    
    if cr.was_answered is None:
        # Verify that the request has an answer
        return HttpResponseRedirect(reverse("toima:home"))

    if cr.was_read is not None:
        # Verify that the request is still unread
        return HttpResponseRedirect(reverse("toima:home"))
    
    cr.was_read = timezone.now()
    cr.save()
    return HttpResponseRedirect(reverse("toima:home"))

@login_required
def messaging(request, us_id):
    # Get the contact if the contact is in user's contact set
    try:
        contact = request.user.contact_set.get(contact__pk=us_id).contact
    except ObjectDoesNotExist:
        raise Http404("Contact does not exist")
    
    # Get messages sent between user and the contact
    messages = Message.objects.filter(
        Q(Q(sender=request.user) & Q(receiver=contact)) |
        Q(Q(sender=contact) & Q(receiver=request.user))
    ).order_by("-was_sent")

    # Count new messages and mark them as read
    timestamp = timezone.now()
    new_count = 0
    for msg in messages:
        if msg.receiver == request.user and msg.was_read is None:
            new_count += 1
            msg.was_read = timestamp
            msg.save()
        else:
            break
    
    # Context
    context = {
        'user': request.user,
        'contact': contact,
        'messages': messages,
        'new_count': new_count}

    return render(
        request, 'toima/messaging.html', context)


# FLAW 4 Step 1: rename the view as messagingSend2
@login_required
def messagingSend(request, us_id):
    msg = request.POST.get("msg")
    if msg is None:
        msg = ''
    else:
        msg = msg.replace("'", "''")

    sqlite3.connect("db.sqlite3").cursor().executescript(
        f" \
        INSERT INTO toima_message ( \
            sender_id, was_sent, msg, receiver_id) \
        VALUES ( \
            {request.user.id}, current_timestamp, '{msg}', {us_id})"
    )

    return HttpResponseRedirect(reverse(
        "toima:messaging", kwargs={'us_id': int(us_id)}))

# FLAW 4 Step 2: rename the view as messagingSend
@login_required
def messagingSend2(request, us_id):
    try:
        contact = request.user.contact_set.get(contact__pk=us_id).contact
    except ValueError:
        raise Http404("Contact does not exist")
    except ObjectDoesNotExist:
        raise Http404("Contact does not exist")

    Message.objects.create(
        sender=request.user,
        receiver=contact,
        msg=request.POST.get("msg")
    ).save()

    return HttpResponseRedirect(reverse("toima:messaging", kwargs={'us_id': us_id}))
