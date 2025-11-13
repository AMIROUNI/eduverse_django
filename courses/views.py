from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from courses.models import Course
from .forms import CourseForm, CategoryForm

from django.contrib import messages

@login_required
def create_course_with_category(request):
    if request.method == 'POST':
        course_form = CourseForm(request.POST, request.FILES)
        category_form = CategoryForm(request.POST)
        if course_form.is_valid() and category_form.is_valid():
            category = category_form.save()
            course = course_form.save(commit=False)
            course.category = category
            course.instructor = request.user
            course.save()
            messages.success(request, 'Course created successfully!')
    else:
        course_form = CourseForm()
        category_form = CategoryForm()

    courses = Course.objects.filter(instructor=request.user)
    return render(request, 'courses/manage_course.html', {
        'course_form': course_form,
        'category_form': category_form,
        'courses': courses
    })

def course_success(request):
    Course= request.course
    return render(request, 'courses/course_success.html', {'course': Course})