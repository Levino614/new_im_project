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
    # DASHBOARD / INDEX / HOME
    path('', views.dashboard_no_id),
    path('dashboard/', views.dashboard_no_id),
    path('dashboard/<int:id>', views.dashboard),

    # DATA CRUD (CREATE/READ/UPDATE/DELETE)
    path('data/', views.data),

    # TIMESHEETS
    path('employee_time/', views.employee_time_no_id),
    path('employee_time/<int:id>', views.employee_time),
    path('task_time/', views.task_time_no_id),
    path('task_time/<int:id>', views.task_time),

    # ADD NEW OBJECTS
    path('add_new_emp/', views.add_new_emp),
    path('add_new_proj/', views.add_new_proj),
    path('add_new_pos/', views.add_new_pos),
    path('add_new_chair/', views.add_new_chair),
    path('add_new_ass/', views.add_new_ass),

    # EDIT OBJECTS
    path('edit_emp/<int:id>', views.edit_emp),
    path('edit_task/<int:id>', views.edit_task),
    path('edit_proj/<int:id>', views.edit_proj),
    path('edit_pos/<int:id>', views.edit_pos),
    path('edit_chair/<int:id>', views.edit_chair),
    path('edit_ass/<int:id>', views.edit_ass),

    # UPDATE OBJECTS
    path('update_emp/<int:id>', views.update_emp),
    path('update_proj/<int:id>', views.update_proj),
    path('update_pos/<int:id>', views.update_pos),
    path('update_chair/<int:id>', views.update_chair),
    path('update_ass/<int:id>', views.update_ass),

    # DELETE OBJECTS
    path('delete_emp/<int:id>', views.delete_emp),
    path('delete_proj/<int:id>', views.delete_proj),
    path('delete_pos/<int:id>', views.delete_pos),
    path('delete_chair/<int:id>', views.delete_chair),
    path('delete_ass/<int:id>', views.delete_ass),

    # ADMIN
    path('admin/', admin.site.urls),

    # EMPLOYEE/TASK WORKLOAD IN SPECIFIC MONTH
    path('employee_in_months/<int:emp_id>/', views.employee_in_months_no_id),
    path('employee_in_months/<int:emp_id>/<int:month_id>', views.employee_in_months),
    path('task_in_months/<int:tsk_id>/', views.task_in_months_no_id),
    path('task_in_months/<int:tsk_id>/<int:month_id>', views.task_in_months),
]
