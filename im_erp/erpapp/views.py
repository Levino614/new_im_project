from django.shortcuts import render, redirect
from erpapp.forms import EmployeeForm, ProjectForm, PositionForm, ChairForm, AssignmentForm
from erpapp.models import Employee, Project, Position, Chair, Assignment, Task


# Create your views here.
def index(request):
    employees = Employee.objects.all()
    projects = Project.objects.all()
    tasks = Task.objects.all()
    assignments = Assignment.objects.all()

    project_infos = []
    employee_infos = []
    for project in projects:
        sum = 0
        ressources = project.ressources
        title = project.title
        for assignment in assignments:
            if assignment.task.id == project.id:
                sum += assignment.percentage
        diff = int(round((sum - ressources), 2) * 100)

        project_infos.append((sum, ressources, title, diff))

        # Employees information
        for employee in employees:
            employee_sum = 0
            for task in tasks:
                for assignment in assignments:
                    if assignment.task.id == task.id and assignment.employee.id == employee.id:
                        employee_sum += assignment.percentage
            overload = int(round((employee_sum - employee.capacity), 2) * 100)
            employee_infos.append((employee, employee_sum, employee.capacity, overload))
        print(employee_infos)

    context = {
        'employees': employees,
        'projects': projects,
        'project_infos': project_infos,
        'employee_infos': employee_infos
    }
    return render(request, 'index.html', context)


def employee(request):
    employees = Employee.objects.all()
    context = {
        'employees': employees
    }
    return render(request, 'employee.html', context)


def task(request):
    projects = Project.objects.all()
    positions = Position.objects.all()
    chairs = Chair.objects.all()
    context = {
        'projects': projects,
        'positions': positions,
        'chairs': chairs
    }
    return render(request, 'tasks.html', context)


def assignment(request):
    assignments = Assignment.objects.all()
    context = {
        'assignments': assignments
    }
    return render(request, 'assignment.html', context)


def timesheet(request):
    employees = Employee.objects.all()
    assignments = Assignment.objects.all()
    projects = Project.objects.all()
    chairs = Chair.objects.all()
    positions = Position.objects.all()
    tasks = Task.objects.all()
    employee_tasks = []
    employee_chairs_tasks = []
    employee_positions_tasks = []
    tasks_sum = []

    # Loop through Project Tasks
    for employee in employees:
        employee_prj_hours = []
        employee_prj_hours_id = []
        for project in projects:
            for assignment in assignments:
                if assignment.task.id == project.id and assignment.employee.id == employee.id:
                    employee_prj_hours.append((int(round(assignment.percentage, 2) * 100), assignment.id, assignment.responsibility))
                    employee_prj_hours_id.append(project.id)
        employee_list_project = []
        for project in projects:
            if project.id in employee_prj_hours_id:
                employee_list_project.append(employee_prj_hours[employee_prj_hours_id.index(project.id)])
            else:
                employee_list_project.append('-')
        employee_tasks.append(employee_list_project)

    # Loop through Chair Tasks
    for employee in employees:
        employee_ch_hours = []
        employee_ch_hours_id = []
        for chair in chairs:
            for assignment in assignments:
                if assignment.task.id == chair.id and assignment.employee.id == employee.id:
                    employee_ch_hours.append((int(round(assignment.percentage, 2) * 100), assignment.id, assignment.responsibility))
                    employee_ch_hours_id.append(chair.id)
        employee_list_chair = []
        for chair in chairs:
            if chair.id in employee_ch_hours_id:
                employee_list_chair.append(employee_ch_hours[employee_ch_hours_id.index(chair.id)])
            else:
                employee_list_chair.append('-')
        employee_chairs_tasks.append(employee_list_chair)
    i = 0
    # And append information to list
    while i < len(employee_tasks):
        j = 0
        while j < len(employee_chairs_tasks[i]):
            employee_tasks[i].append(employee_chairs_tasks[i][j])
            j = j + 1
        i = i + 1

    # Loop through Position Tasks
    for employee in employees:  # For Project start
        employee_pos_hours = []
        employee_pos_hours_id = []
        for position in positions:
            for assignment in assignments:
                if assignment.task.id == position.id and assignment.employee.id == employee.id:
                    employee_pos_hours.append((int(round(assignment.percentage, 2) * 100), assignment.id, assignment.responsibility))
                    employee_pos_hours_id.append(position.id)
        employee_list_position = []
        for position in positions:
            if position.id in employee_pos_hours_id:
                employee_list_position.append(employee_pos_hours[employee_pos_hours_id.index(position.id)])
            else:
                employee_list_position.append('-')
        employee_positions_tasks.append(employee_list_position)
    ii = 0
    # And append information to list
    while ii < len(employee_tasks):
        jj = 0
        while jj < len(employee_positions_tasks[ii]):
            employee_tasks[ii].append(employee_positions_tasks[ii][jj])
            jj = jj + 1
        ii = ii + 1

    # Used ressources, summed up for each project
    for project in projects:
        sum = 0
        for assignment in assignments:
            if assignment.task.id == project.id:
                sum += assignment.percentage

        tasks_sum.append(int(round(sum, 2) * 100))

    # Append (employee, workload)-Tuple employee_infos list
    employee_infos = []
    for employee in employees:
        employee_sum = 0
        for task in tasks:
            for assignment in assignments:
                if assignment.task.id == task.id and assignment.employee.id == employee.id:
                    employee_sum += assignment.percentage
        workload = employee_sum / employee.capacity
        employee_infos.append((employee, int(round(employee_sum, 2) * 100), int(round(employee.capacity, 2) * 100), workload))
    print(employee_infos)
    context = {
        'employees': employees,
        'assignments': assignments,
        'projects': projects,
        'chairs': chairs,
        'positions': positions,
        'employeetasks': employee_tasks,
        'tasks_sum': tasks_sum,
        'employee_infos': employee_infos
    }
    return render(request, 'timesheet.html', context)


def add_new_emp(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/employee')
    else:
        form = EmployeeForm()
    context = {
        'form': form
    }
    return render(request, 'add_new_emp.html', context)


def add_new_proj(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/tasks')
    else:
        form = ProjectForm()
    context = {
        'form': form
    }
    return render(request, 'add_new_proj.html', context)


def add_new_pos(request):
    if request.method == "POST":
        form = PositionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/tasks')
    else:
        form = PositionForm()
    context = {
        'form': form
    }
    return render(request, 'add_new_pos.html', context)


def add_new_chair(request):
    if request.method == "POST":
        form = ChairForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/tasks')
    else:
        form = ChairForm()
    context = {
        'form': form
    }
    return render(request, 'add_new_chair.html', context)


def add_new_ass(request):
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/assignments')
    else:
        form = AssignmentForm()
    context = {
        'form': form
    }
    return render(request, 'add_new_ass.html', context)


def edit_emp(request, id):
    employee = Employee.objects.get(id=id)
    context = {
        'employee': employee
    }
    return render(request, 'edit_emp.html', context)


def edit_proj(request, id):
    project = Project.objects.get(id=id)
    context = {
        'project': project
    }
    return render(request, 'edit_proj.html', context)


def edit_pos(request, id):
    position = Position.objects.get(id=id)
    context = {
        'position': position
    }
    return render(request, 'edit_pos.html', context)


def edit_chair(request, id):
    chair = Chair.objects.get(id=id)
    context = {
        'chair': chair
    }
    return render(request, 'edit_chair.html', context)


def edit_ass(request, id):
    assignment = Assignment.objects.get(id=id)
    context = {
        'assignment': assignment
    }
    return render(request, 'edit_ass.html', context)


def update_emp(request, id):
    employee = Employee.objects.get(id=id)
    form = EmployeeForm(request.POST, instance=employee)
    if form.is_valid():
        form.save()
        return redirect('/employee')
    context = {
        'employee': employee
    }
    return render(request, 'edit_emp.html', context)


def update_proj(request, id):
    project = Project.objects.get(id=id)
    form = ProjectForm(request.POST, instance=project)
    if form.is_valid():
        form.save()
        return redirect('/tasks')
    context = {
        'project': project
    }
    return render(request, 'edit_proj.html', context)


def update_pos(request, id):
    position = Position.objects.get(id=id)
    form = PositionForm(request.POST, instance=position)
    if form.is_valid():
        form.save()
        return redirect('/tasks')
    context = {
        'position': position
    }
    return render(request, 'edit_pos.html', context)


def update_chair(request, id):
    chair = Chair.objects.get(id=id)
    form = ChairForm(request.POST, instance=chair)
    if form.is_valid():
        form.save()
        return redirect('/tasks')
    context = {
        'chair': chair
    }
    return render(request, 'edit_chair.html', context)


def update_ass(request, id):
    chair = Assignment.objects.get(id=id)
    form = AssignmentForm(request.POST, instance=assignment)
    if form.is_valid():
        form.save()
        return redirect('/assignments')
    context = {
        'assignment': assignment
    }
    return render(request, 'edit_ass.html', context)


def delete_emp(request, id):
    employee = Employee.objects.get(id=id)
    employee.delete()
    return redirect('/employee')


def delete_proj(request, id):
    project = Project.objects.get(id=id)
    project.delete()
    return redirect('/tasks')


def delete_pos(request, id):
    position = Position.objects.get(id=id)
    position.delete()
    return redirect('/tasks')


def delete_chair(request, id):
    chair = Chair.objects.get(id=id)
    chair.delete()
    return redirect('/tasks')


def delete_ass(request, id):
    assignment = Assignment.objects.get(id=id)
    assignment.delete()
    return redirect('/assignments')
