from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from courses.models import Course
from .forms import CourseForm, CategoryForm, SectionForm , LessonForm
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from .models import Course , Section

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





def course_detail(request, course_id):
    if request.method  == 'POST':
        section_form = SectionForm(request.POST)
        if section_form.is_valid():
            section = section_form.save(commit=False)
            section.course_id = course_id
            section.save()
            messages.success(request, 'Section added successfully!')
    course = get_object_or_404(Course, id=course_id)
    sections = Section.objects.filter(course=course)
    return render(request, 'courses/course_detail.html', {'course': course, 'section_form': SectionForm(), 'sections': sections})




def section_detail(request, section_id):
    if request.method == 'POST':
       form_lesson = LessonForm(request.POST, request.FILES)
       if form_lesson.is_valid():
           lesson = form_lesson.save(commit=False)
           lesson.section_id = section_id
           lesson.save()
           messages.success(request, 'Lesson added successfully!')  
    section = get_object_or_404(Section, id=section_id)
    lessons = section.lessons.all()
    return render(request, 'courses/lesson_list.html', {'section': section, 'lessons': lessons, 'lesson_form': LessonForm()})