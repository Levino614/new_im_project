"""im_erp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from erpapp import views

urlpatterns = [
    path('', views.index),
    path('employee/', views.employee),
    path('tasks/', views.task),
    path('assignments/', views.assignment),
    path('employee_task/', views.employee_task_no_id),
    path('employee_task/<int:id>', views.employee_task),
    path('employee_time/', views.employee_time_no_id),
    path('employee_time/<int:id>', views.employee_time),
    path('task_time/', views.task_time_no_id),
    path('task_time/<int:id>', views.task_time),
    path('add_new_emp/', views.add_new_emp),
    path('add_new_proj/', views.add_new_proj),
    path('add_new_pos/', views.add_new_pos),
    path('add_new_chair/', views.add_new_chair),
    path('add_new_ass/', views.add_new_ass),
    path('edit_emp/<int:id>', views.edit_emp),
    path('edit_task/<int:id>', views.edit_task),
    path('edit_proj/<int:id>', views.edit_proj),
    path('edit_pos/<int:id>', views.edit_pos),
    path('edit_chair/<int:id>', views.edit_chair),
    path('edit_ass/<int:id>', views.edit_ass),
    path('update_emp/<int:id>', views.update_emp),
    path('update_proj/<int:id>', views.update_proj),
    path('update_pos/<int:id>', views.update_pos),
    path('update_chair/<int:id>', views.update_chair),
    path('update_ass/<int:id>', views.update_ass),
    path('delete_emp/<int:id>', views.delete_emp),
    path('delete_proj/<int:id>', views.delete_proj),
    path('delete_pos/<int:id>', views.delete_pos),
    path('delete_chair/<int:id>', views.delete_chair),
    path('delete_ass/<int:id>', views.delete_ass),
    path('admin/', admin.site.urls),
    path('test/', views.test),
    path('employee_in_months/<int:emp_id>/', views.employee_in_months_no_id),
    path('employee_in_months/<int:emp_id>/<int:month_id>', views.employee_in_months),
    path('task_in_months/<int:tsk_id>/', views.task_in_months_no_id),
    path('task_in_months/<int:tsk_id>/<int:month_id>', views.task_in_months),
    path('test/<int:id>', views.test),
]
