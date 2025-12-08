from django.urls import path
from . import views


urlpatterns = [
    path('manage/', views.create_course_with_category, name='manage_course'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('section/<int:section_id>/', views.section_detail, name='section_detail'), 
    path('<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('my_courses/', views.my_courses, name='my_courses'),
    path('pdf/<int:pdf_id>/generate-quiz/', views.generate_quiz, name='generate_quiz'),
    path('pdf/<int:pdf_id>/take-quiz/', views.take_quiz, name='take_quiz'),
    path('pdf/<int:pdf_id>/save-quiz/', views.save_quiz, name='save_quiz'),




    path('test-gemini/', views.test_gemini_models, name='test_gemini'),



    path('section/<int:section_id>/delete/', views.delete_section, name='delete_section'),
    path('section/<int:section_id>/edit/', views.edit_section, name='edit_section'),
    path('', views.courses, name='courses')]   