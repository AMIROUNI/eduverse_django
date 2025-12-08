from django.db import models
from django.conf import settings
from users.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'instructor'})
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    students = models.ManyToManyField(User, related_name='my_courses', blank=True)


class Section(models.Model):
    course = models.ForeignKey(Course, related_name='sections', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

class Lesson(models.Model):
    section = models.ForeignKey(Section, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    pdf_file = models.FileField(upload_to='lessons/pdfs/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    duration = models.DurationField(null=True, blank=True)

class PDFMaterial(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='pdf_materials')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='course_pdfs/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ADD THIS
    uploaded_at = models.DateTimeField(auto_now_add=True)
   

class Quiz(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='quizzes')
    pdf = models.ForeignKey('PDFMaterial', on_delete=models.CASCADE, related_name='quizzes')
    question = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=1, choices=[
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Quiz from {self.pdf.title}"