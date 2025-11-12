
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm

def signUp(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {user}!')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'users/signup.html', {'form': form})
