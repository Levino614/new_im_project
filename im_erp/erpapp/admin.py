from django.contrib import admin
from .models import Employee, Project, Position, Chair, Task

# Register your models here.
admin.site.register(Employee)
admin.site.register(Project)
admin.site.register(Position)
admin.site.register(Chair)
admin.site.register(Task)
