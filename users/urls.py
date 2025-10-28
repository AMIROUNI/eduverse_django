from django.urls import path
from users.views import signUp



urlpatterns = [
    path('signup/', signUp, name='signup'),
]
