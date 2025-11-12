from django.contrib import admin

# Register your models here.

from .models import Choice
from .models import Question
from .models import Quiz
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Choice)
