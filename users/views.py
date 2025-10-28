from urllib import request
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
# Create your views here.



def signUp(request):
    if request.method == 'POST' :
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {user}!')
            return render(request, 'users/login.html')
    else:
        form = UserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

