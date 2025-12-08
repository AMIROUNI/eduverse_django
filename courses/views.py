from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from courses.models import Course
from .forms import CourseForm, CategoryForm, SectionForm , LessonForm
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from .models import Course, PDFMaterial , Section , Quiz
from enrollments.models import Enrollment
from .utils import extract_text_from_pdf, generate_quiz_from_pdf


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

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    sections = Section.objects.filter(course=course)
    
    # DEBUG: Print to terminal
    print(f"\n{'='*50}")
    print(f"DEBUG: course_detail view called for course_id={course_id}")
    print(f"Course: {course.title} (ID: {course.id})")
    print(f"Number of PDFs found: {course.pdf_materials.count()}")
    
    # Initialize forms
    section_form = SectionForm()
    
    if request.method == 'POST':
        # Check which form was submitted
        if 'form_type' in request.POST:
            if request.POST['form_type'] == 'pdf_upload':
                # Handle PDF upload
                title = request.POST.get('pdf_title')
                pdf_file = request.FILES.get('pdf_file')
                
                if title and pdf_file:
                    # Check if user is instructor
                    if request.user == course.instructor:
                        # Check file extension
                        if not pdf_file.name.lower().endswith('.pdf'):
                            messages.error(request, "Only PDF files are allowed.")
                        else:
                            # Check file size (optional - 10MB limit)
                            if pdf_file.size > 10 * 1024 * 1024:  # 10MB
                                messages.error(request, "File size exceeds 10MB limit.")
                            else:
                                # Create PDF material
                                PDFMaterial.objects.create(
                                    course=course,
                                    title=title,
                                    file=pdf_file,
                                    uploaded_by=request.user
                                )
                                messages.success(request, f'PDF "{title}" uploaded successfully!')
                    else:
                        messages.error(request, "Only instructors can upload materials.")
                else:
                    messages.error(request, "Please provide both title and PDF file.")
                
                return redirect('course_detail', course_id=course_id)
            
            elif request.POST['form_type'] == 'generate_quiz':
                # Redirect to the separate quiz generation page
                pdf_id = request.POST.get('pdf_id')
                if pdf_id:
                    try:
                        pdf = PDFMaterial.objects.get(id=pdf_id, course=course)
                        # Redirect to the dedicated quiz generation page
                        return redirect('generate_quiz', pdf_id=pdf.id)
                    except PDFMaterial.DoesNotExist:
                        messages.error(request, "Selected PDF not found.")
                else:
                    messages.error(request, "Please select a PDF to generate quiz from.")
                
                return redirect('course_detail', course_id=course_id)
        
        else:
            # Handle section form (no form_type specified)
            section_form = SectionForm(request.POST)
            if section_form.is_valid():
                # Check if user is instructor
                if request.user == course.instructor:
                    section = section_form.save(commit=False)
                    section.course = course
                    section.save()
                    messages.success(request, 'Section added successfully!')
                    return redirect('course_detail', course_id=course_id)
                else:
                    messages.error(request, 'Only instructors can add sections.')
    
    # Count total lessons
    total_lessons = 0
    for section in sections:
        total_lessons += section.lessons.count()
    
    # Calculate section progress for students
    if request.user.role == 'student' and request.user in course.students.all():
        # Add progress information to each section
        for section in sections:
            # This is a placeholder - you'll need to implement actual progress tracking
            # based on your lesson completion model
            section.progress = 0  # Default to 0%
            # If you have a Progress model, calculate actual progress here
    
    context = {
        'course': course,
        'sections': sections,
        'section_form': section_form,
        'total_lessons': total_lessons,
    }
    
    return render(request, 'courses/course_detail.html', context)
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


@login_required
def delete_section(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    course_id = section.course.id
    section.delete()
    messages.success(request, 'Section deleted successfully!')
    return redirect('course_detail', course_id=course_id)



def edit_section(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    if request.method == 'POST':
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, 'Section updated successfully!')
            return redirect('course_detail', course_id=section.course.id)
    else:
        form = SectionForm(instance=section)
    return render(request, 'courses/edit_section.html', {'form': form, 'section': section})

@login_required
def courses(request):
    all_courses = Course.objects.all()
    return render(request, 'courses/courses.html', {'courses': all_courses})


@login_required
def courses(request):
    query = request.GET.get('q', '')  # get ?q= from URL
    if query:
        results = Course.objects.filter(title__icontains=query)  # case-insensitive search
    else:
        results = Course.objects.all()
    return render(request, 'courses/courses.html', {'query': query, 'courses': results})



@login_required
def enroll_course(request, course_id):
    print("enrollment://///////////////////////////", course_id)
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        if request.user not in course.students.all():
            course.students.add(request.user)
            print("Added:", request.user)

    return redirect('my_courses')


@login_required
def my_courses(request):
    courses = request.user.my_courses.all()  # fetch all courses where user is enrolled
    return render(request, 'courses/my_courses.html', {'courses': courses})






@login_required
def generate_quiz(request, pdf_id):
    """Generate quiz from PDF and display it"""
    pdf = get_object_or_404(PDFMaterial, id=pdf_id)
    course = pdf.course
    
    # Check if user is instructor
    if request.user != course.instructor:
        messages.error(request, "Only instructors can generate quizzes.")
        return redirect('course_detail', course_id=course.id)
    
    # Check if quizzes already exist
    existing_quizzes = Quiz.objects.filter(pdf=pdf)
    
    if request.method == 'POST':
        # Generate new quizzes
        try:
            # Extract text from PDF
            pdf_text = extract_text_from_pdf(pdf.file)
            
            if not pdf_text:
                messages.error(request, "Could not extract text from PDF.")
                return redirect('generate_quiz', pdf_id=pdf.id)
            
            # Generate quizzes using Gemini
            quizzes_data = generate_quiz_from_pdf(
                pdf_text, 
                course.title, 
                course.instructor.username,
                pdf.title
            )
            
            # Delete existing quizzes
            existing_quizzes.delete()
            
            # Save new quizzes
            for quiz_data in quizzes_data:
                Quiz.objects.create(
                    course=course,
                    pdf=pdf,
                    question=quiz_data.get('question', ''),
                    option_a=quiz_data.get('option_a', ''),
                    option_b=quiz_data.get('option_b', ''),
                    option_c=quiz_data.get('option_c', ''),
                    option_d=quiz_data.get('option_d', ''),
                    correct_answer=quiz_data.get('correct_answer', 'A')
                )
            
            messages.success(request, f"Generated {len(quizzes_data)} quizzes successfully!")
            
        except Exception as e:
            messages.error(request, f"Error generating quizzes: {str(e)}")
    
    # Get current quizzes
    quizzes = Quiz.objects.filter(pdf=pdf)
    
    context = {
        'course': course,
        'pdf': pdf,
        'quizzes': quizzes,
        'has_quizzes': quizzes.exists(),
    }
    
    return render(request, 'courses/quiz.html', context)

@login_required
def take_quiz(request, pdf_id):
    """Page for students to take the quiz"""
    pdf = get_object_or_404(PDFMaterial, id=pdf_id)
    course = pdf.course
    
    # Check if student is enrolled
    if request.user not in course.students.all() and request.user != course.instructor:
        messages.error(request, "You must be enrolled in this course to take the quiz.")
        return redirect('course_detail', course_id=course.id)
    
    quizzes = Quiz.objects.filter(pdf=pdf)
    
    if request.method == 'POST':
        # Calculate score
        score = 0
        total = quizzes.count()
        
        for quiz in quizzes:
            user_answer = request.POST.get(f'quiz_{quiz.id}')
            if user_answer == quiz.correct_answer:
                score += 1
        
        context = {
            'course': course,
            'pdf': pdf,
            'score': score,
            'total': total,
            'percentage': (score / total * 100) if total > 0 else 0,
        }
        
        return render(request, 'courses/quiz_result.html', context)
    
    context = {
        'course': course,
        'pdf': pdf,
        'quizzes': quizzes,
    }
    
    return render(request, 'courses/take_quiz.html', context)

# Add this to your views.py

@login_required
def save_quiz(request, pdf_id):
    """Save generated quizzes to database"""
    pdf = get_object_or_404(PDFMaterial, id=pdf_id)
    course = pdf.course
    
    # Check if user is instructor
    if request.user != course.instructor:
        messages.error(request, "Only instructors can save quizzes.")
        return redirect('generate_quiz', pdf_id=pdf.id)
    
    # Check if there are generated quizzes in session
    # OR you might want to pass quiz data differently
    
    # For now, we'll redirect back
    messages.success(request, "Quizzes saved to database successfully!")
    return redirect('generate_quiz', pdf_id=pdf.id)



# In your views.py

@login_required
def take_quiz(request, pdf_id):
    """View for students to take a quiz"""
    pdf = get_object_or_404(PDFMaterial, id=pdf_id)
    course = pdf.course
    
    # Check if user is enrolled or is instructor
    if request.user not in course.students.all() and request.user != course.instructor:
        messages.error(request, "You must be enrolled in this course to take the quiz.")
        return redirect('course_detail', course_id=course.id)
    
    # Get quizzes for this PDF
    quizzes = Quiz.objects.filter(pdf=pdf)
    
    if not quizzes.exists():
        messages.error(request, "No quizzes available for this PDF yet.")
        return redirect('course_detail', course_id=course.id)
    
    # Handle quiz submission
    if request.method == 'POST':
        score = 0
        total = quizzes.count()
        user_answers = {}
        
        # Calculate score
        for quiz in quizzes:
            user_answer = request.POST.get(f'quiz_{quiz.id}')
            user_answers[quiz.id] = user_answer
            
            if user_answer == quiz.correct_answer:
                score += 1
        
        # Calculate percentage
        percentage = (score / total * 100) if total > 0 else 0
        
        context = {
            'course': course,
            'pdf': pdf,
            'quizzes': quizzes,
            'user_answers': user_answers,
            'score': score,
            'total': total,
            'percentage': percentage,
            'show_results': True,
        }
        
        return render(request, 'courses/take_quiz.html', context)
    
    # GET request - show the quiz form
    context = {
        'course': course,
        'pdf': pdf,
        'quizzes': quizzes,
        'show_results': False,
    }
    
    return render(request, 'courses/take_quiz', context)







# courses/views.py - Add this function

import google.generativeai as genai
import os
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def test_gemini_models(request):
    """Test endpoint to check available Gemini models"""
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        return JsonResponse({
            'error': 'GEMINI_API_KEY not found in environment variables'
        }, status=400)
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # List all available models
        models = []
        for model in genai.list_models():
            model_info = {
                'name': model.name,
                'description': model.description,
                'display_name': model.display_name,
                'supported_generation_methods': model.supported_generation_methods,
                'input_token_limit': getattr(model, 'input_token_limit', None),
                'output_token_limit': getattr(model, 'output_token_limit', None),
            }
            models.append(model_info)
        
        # Try to generate content with popular models to test
        test_results = []
        popular_models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
        
        for model_name in popular_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello, are you working?")
                test_results.append({
                    'model': model_name,
                    'status': 'SUCCESS',
                    'test_response': response.text[:100] if response.text else 'No text response'
                })
            except Exception as e:
                test_results.append({
                    'model': model_name,
                    'status': 'FAILED',
                    'error': str(e)
                })
        
        return JsonResponse({
            'api_key_status': 'VALID',
            'total_models': len(models),
            'all_models': models,
            'popular_models_test': test_results,
            'instructions': 'Use "gemini-1.5-flash" for fast responses or "gemini-1.5-pro" for better quality'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'api_key_status': 'INVALID or ERROR'
        }, status=500)