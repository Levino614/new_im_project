from django.shortcuts import render, redirect
from erpapp.forms import EmployeeForm
from erpapp.models import Employee


# Create your views here.
def index(request):
    return render(request, 'index.html')


def employee(request):
    employees = Employee.objects.all()
    return render(request, 'employee.html', {'employees': employees})


def add_new_emp(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = EmployeeForm()
    context = {
        'form': form
    }
    return render(request, 'add_new_emp.html', context)


def edit_emp(request, id):
    employee = Employee.objects.get(id=id)
    context = {
        'employee': employee
    }
    return render(request, 'edit_emp.html', context)


def update_emp(request, id):
    employee = Employee.objects.get(id=id)
    form = EmployeeForm(request.POST, instance=employee)
    if form.is_valid():
        form.save()
        return redirect('/')
    context = {
        'employee': employee
    }
    return render(request, 'edit_emp.html', context)


def delete_emp(request, id):
    employee = Employee.objects.get(id=id)
    employee.delete()
    return redirect('/')
