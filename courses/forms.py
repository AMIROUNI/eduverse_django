
from django import forms
from .models import Course, Section, Lesson, Category


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description'   , 'price', 'thumbnail']

class SectionForm(forms.ModelForm):
    class Meta:
        model =  Section
        fields = ['course', 'title', 'order']
class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['section', 'title', 'content', 'video_url', 'pdf_file', 'order', 'duration']
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']




