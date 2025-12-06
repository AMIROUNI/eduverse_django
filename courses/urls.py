from django.urls import path
from . import views


urlpatterns = [
    path('manage/', views.create_course_with_category, name='manage_course'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('section/<int:section_id>/', views.section_detail, name='section_detail'), 

    path('section/<int:section_id>/delete/', views.delete_section, name='delete_section'),
    path('section/<int:section_id>/edit/', views.edit_section, name='edit_section'),
path('', views.courses, name='courses')]   