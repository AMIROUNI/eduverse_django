from django.urls import path
from . import views


urlpatterns = [
    path('manage/', views.create_course_with_category, name='manage_course'),
    path('success/', views.course_success, name='course_success'),
]