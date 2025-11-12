
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm, UserAvatarForm

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




def profile_upload_avatar(request):
    if request.method == 'POST':
        form = UserAvatarForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # or any page
    else:
        form = UserAvatarForm(instance=request.user)

    return render(request, 'users/profile.html', {'form': form})




def profile(request):
    # request.user contains the currently logged-in user object
    user = request.user  

    # Pass the user object to the template
    return render(request, 'users/profile.html', {'user': user})