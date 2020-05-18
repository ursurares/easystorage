from django.shortcuts import render,redirect
from django_registration import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            
            username=form.cleaned_data.get('username')
            messages.success(request,f'Account created for {username}!')
            return redirect('http://127.0.0.1:8000/store/')
            #form.save()
    else:
        form = UserCreationForm()

    return render(request,'accounts/register.html',
    {
        'form':form,
        })
