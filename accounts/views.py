from django.shortcuts import render,redirect
from django_registration import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string

from .tokens import account_activation_token
from .forms import RegisterForm


def activation_sent_view(request):
    return render(request, 'activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token):
        # if valid set active true 
        user.is_active = True
        # set signup_confirmation true
        user.account.register_confirmation = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'activation_invalid.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.refresh_from_db()
            user.account.first_name=form.cleaned_data.get('first_name')
            user.account.last_name=form.cleaned_data.get('last_name')
            user.account.email=form.cleaned_data.get('email')
            user.is_active = False
            user.save()
            current_page=get_current_site(request)
            message= render_to_string('activation_request.html',{
                'user':user,
                'domain':current_page.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            user.email_user('EasyStore Account Activation',message)
            return redirect('activation_sent')
    else:
        form = UserCreationForm()

    return render(request,'accounts/register.html',
    {
        'form':form,
        })
