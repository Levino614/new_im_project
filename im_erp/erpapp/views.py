from datetime import datetime

from django.shortcuts import render, redirect
from django.utils import timezone
from erpapp.forms import EmployeeForm, ProjectForm, PositionForm, ChairForm, AssignmentForm, EditAssignmentForm, \
    MonthForm
from django.contrib import messages
from erpapp.models import Employee, Project, Position, Chair, Assignment, Task, Month, AssignmentPerMonth


# DATA CRUD (CREATE/READ/UPDATE/DELETE)
def data(request):
    employees = Employee.objects.all()
    projects = Project.objects.all()
    positions = Position.objects.all()
    chairs = Chair.objects.all()
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

        # Collect Employees Information
        # (Employee, summed assignment percentages, max Capacity and the difference between them)
        for employee in employees:
            employee_sum = 0
            for task in tasks:
                for assignment in assignments:
                    if assignment.task.id == task.id and assignment.employee.id == employee.id:
                        employee_sum += assignment.percentage
            overload = int(round((employee_sum - employee.capacity), 2) * 100)
            employee_infos.append((employee, employee_sum, employee.capacity, overload))

    warnings = []
    for project_info in project_infos:
        if project_info[0] > project_info[1]:
            warnings.append('{} is currently using too many ressources! ({}%)'.format(project_info[2], project_info[3]))
    for employee_info in employee_infos:
        if employee_info[1] > employee_info[2]:
            warnings.append('{} is currently working too many hours! ({}%)'.format(employee_info[0], employee_info[3]))
    warnings_length = len(warnings)
    context = {
        'employees': employees,
        'projects': projects,
        'positions': positions,
        'chairs': chairs,
        'project_infos': project_infos,
        'employee_infos': employee_infos,
        'assignments': assignments,
        'warnings': warnings,
        'warnings_length': warnings_length,
    }
    return render(request, 'data.html', context)


# DASHBOARD / INDEX / HOME
def dashboard_no_id(request):
    date = timezone.now()
    current_year, current_month, _ = str(date).split('-')
    month_dict = {
        '1': 'January',
        '2': 'February',
        '3': 'March',
        '4': 'April',
        '5': 'May',
        '6': 'June',
        '7': 'July',
        '8': 'August',
        '9': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December',
    }
    month_name = month_dict[str(int(current_month))]
    month = Month.objects.get(month=month_name, year=current_year)
    return redirect('/dashboard/{}'.format(month.id))


def dashboard(request, id):
    month = Month.objects.get(id=id)
    tasks = Task.objects.all()

    month_dict = {
        '1': 'January',
        '2': 'February',
        '3': 'March',
        '4': 'April',
        '5': 'May',
        '6': 'June',
        '7': 'July',
        '8': 'August',
        '9': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December',
    }
    if request.method == "POST":
        start = request.POST.get('start_month')
        try:
            start_year, start_month = str(start).split('-')
        except ValueError:
            return redirect('/dashboard/')
        for month_obj in Month.objects.all():
            if month_obj.month == month_dict[str(int(start_month))] and month_obj.year == start_year:
                month_id = month_obj.id
                return redirect('/dashboard/{}'.format(month_id))
        return redirect('/dashboard/')

    # list for all employees
    employee_rows = []

    # create a list for each employee
    for employee in Employee.objects.all():
        employee_row = []
        # employee info
        employee_sum = 0
        # look through all assignments for all tasks for one emoloyee
        for task in tasks:
            for assignment_per_month in AssignmentPerMonth.objects.all():
                # if assignment in month exists add percentage to sum
                if employee.id == assignment_per_month.employee.id and task.id == assignment_per_month.task.id and month == assignment_per_month.month:
                    employee_sum = employee_sum + assignment_per_month.percentage
        # get capacity and calculate workload
        employee_capacity = employee.capacity
        employee_worklooad = employee_sum / employee_capacity

        # attach these infos to first element in list for each employee
        employee_title = [(employee, int(employee_sum * 100), int(employee_capacity * 100), employee_worklooad)]

        # GET A LIST WITH '-' FOR EVERY PROJECT
        assignment_infos_project = []
        for counter, project in enumerate(Project.objects.all()):
            assignment_infos_project.append(['-', False])
            # seach assignment for project, employee and selected month
            for assignment_per_month in AssignmentPerMonth.objects.all():
                if employee.id == assignment_per_month.employee.id and project.id == assignment_per_month.task.id and month == assignment_per_month.month:
                    assignment_infos_project[counter] = [int(assignment_per_month.percentage * 100),
                                                         assignment_per_month.responsibility]
        # append it to the row for employee
        employee_title.append(assignment_infos_project)
        # append row to to the matrix for employee_task

        # GET A LIST WITH '-' FOR EVERY POSITION
        assignment_infos_position = []
        for counter, position in enumerate(Position.objects.all()):
            assignment_infos_position.append(['-', False])
            # search assignments for postion, employee and selected month
            for assignment_per_month in AssignmentPerMonth.objects.all():
                if employee.id == assignment_per_month.employee.id and position.id == assignment_per_month.task.id and month == assignment_per_month.month:
                    assignment_infos_position[counter] = [int(assignment_per_month.percentage * 100),
                                                          assignment_per_month.responsibility]
        # append it to the row for employee
        employee_title.append(assignment_infos_position)

        # GET A LIST WITH '-' FOR EVERY CHAIR
        assignment_infos_chair = []
        for counter, chair in enumerate(Chair.objects.all()):
            assignment_infos_chair.append(['-', False])
            # search assignments for chair, employee and selected month
            for assignment_per_month in AssignmentPerMonth.objects.all():
                if employee.id == assignment_per_month.employee.id and chair.id == assignment_per_month.task.id and month == assignment_per_month.month:
                    assignment_infos_chair[counter] = [int(assignment_per_month.percentage * 100),
                                                       assignment_per_month.responsibility]
        # append it to the row for employee
        employee_title.append(assignment_infos_chair)

        employee_rows.append(employee_title)
    print("employee_rows:, ", employee_rows)

    # get all percentages sums for all tasks
    task_sums = []
    for project in Project.objects.all():
        sum = 0
        for assignment_per_month in AssignmentPerMonth.objects.all():
            if project.id == assignment_per_month.task.id and month == assignment_per_month.month:
                sum = sum + assignment_per_month.percentage
        task_sums.append([int(sum * 100), int(project.ressources * 100)])
    for position in Position.objects.all():
        sum = 0
        for assignment_per_month in AssignmentPerMonth.objects.all():
            if position.id == assignment_per_month.task.id and month == assignment_per_month.month:
                sum = sum + assignment_per_month.percentage
        task_sums.append([int(sum * 100), int(position.ressources * 100)])
    for chair in Chair.objects.all():
        sum = 0
        for assignment_per_month in AssignmentPerMonth.objects.all():
            if chair.id == assignment_per_month.task.id and month == assignment_per_month.month:
                sum = sum + assignment_per_month.percentage
        task_sums.append([int(sum + 100), int(chair.requirement * 100)])

    # print("task:sum: ", task_sums)

    # GET INFORMARTION FOR ALL PROJECTS
    task_infos = []
    for project in Project.objects.all():
        sum = 0
        for assignment_per_month in AssignmentPerMonth.objects.all():
            if project.id == assignment_per_month.task.id and month == assignment_per_month.month:
                sum = sum + assignment_per_month.percentage
        task_workload = sum / project.ressources
        task_infos.append([project, int(sum * 100), int(project.ressources * 100), round(task_workload, 2)])

    # print("projects: ", task_infos)

    # GET INFORMARTION FOR ALL POSITIONS
    for position in Position.objects.all():
        sum = 0
        for assignment_per_month in AssignmentPerMonth.objects.all():
            if position.id == assignment_per_month.task.id and month == assignment_per_month.month:
                sum = sum + assignment_per_month.percentage
        task_workload = sum / position.ressources
        task_infos.append([position, int(sum * 100), int(position.ressources * 100), round(task_workload, 2)])

    # print("postions: ", task_infos)

    # GET INFORMATION ABOUT ALL CHAIRS
    for chair in Chair.objects.all():
        sum = 0
        for assignment_per_month in AssignmentPerMonth.objects.all():
            if chair.id == assignment_per_month.task.id and month == assignment_per_month.month:
                sum = sum + assignment_per_month.percentage
        chair_workload = sum / chair.requirement
        task_infos.append([chair, int(sum * 100), int(chair.requirement * 100), round(chair_workload, 2)])

    # print("chairs:,", task_infos)

    date = timezone.now()
    current_year, current_month, _ = str(date).split('-')
    current_month_name = month_dict[str(int(current_month))]
    today = Month.objects.get(month=current_month_name, year=current_year)
    try:
        previous_month = Month.objects.get(id=id - 1)
    except Exception:
        previous_month = Month.objects.get(id=id)
    try:
        next_month = Month.objects.get(id=id + 1)
    except Exception:
        next_month = Month.objects.get(id=id)

    # Warnings and recommendations
    projects = Project.objects.all()
    assignments = Assignment.objects.all()
    employees = Employee.objects.all()
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
    context = {
        'tasks': tasks,
        'task_infos': task_infos,
        'project_infos': project_infos,
        'employee_infos': employee_infos,
        'employee_rows': employee_rows,
        'task_sums': task_sums,
        'month': month,
        'today': today,
        'previous_month': previous_month,
        'next_month': next_month,
    }
    return render(request, 'dashboard.html', context)


# EMPLOYEE/TASK WORKLOAD IN SPECIFIC MONTH
def employee_in_months_no_id(request, emp_id):
    date = timezone.now()
    current_year, current_month, _ = str(date).split('-')
    month_dict = {
        '1': 'January',
        '2': 'February',
        '3': 'March',
        '4': 'April',
        '5': 'May',
        '6': 'June',
        '7': 'July',
        '8': 'August',
        '9': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December',
    }
    month_name = month_dict[str(int(current_month))]
    month = Month.objects.get(month=month_name, year=current_year)
    return redirect('/employee_in_months/{}/{}'.format(emp_id, month.id))


def employee_in_months(request, emp_id, month_id):
    month_dict = {
        '1': 'January',
        '2': 'February',
        '3': 'March',
        '4': 'April',
        '5': 'May',
        '6': 'June',
        '7': 'July',
        '8': 'August',
        '9': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December',
    }
    if request.method == "POST":
        start = request.POST.get('start_month')
        try:
            start_year, start_month = str(start).split('-')
        except ValueError:
            return redirect('/employee_in_months/{}/{}'.format(emp_id, month_id))
        for month_obj in Month.objects.all():
            if month_obj.month == month_dict[str(int(start_month))] and month_obj.year == start_year:
                month_id = month_obj.id
                return redirect('/employee_in_months/{}/{}'.format(emp_id, month_id))
        return redirect('/employee_in_months/{}/{}'.format(emp_id, month_id))

    # data for one employee
    employee = Employee.objects.get(id=emp_id)
    months = Month.objects.all()
    tasks_in_months = []

    for task in Task.objects.all():
        task_info = [task.title]
        assignments = []
        # iterate through all months
        for counter, month in enumerate(Month.objects.all()):
            assignments.append('-')
            for assignment_per_months in AssignmentPerMonth.objects.all():  # set assignment_percentages to right month
                if task.id == assignment_per_months.task.id and employee.id == assignment_per_months.employee.id and month == assignment_per_months.month:
                    assignments[counter] = int(round(assignment_per_months.percentage, 2) * 100)
        task_info.append(assignments[month_id - 1:month_id + 11])
        tasks_in_months.append(task_info)
    months = months[month_id - 1:month_id + 11]

    month_dict = {
        '1': 'January',
        '2': 'February',
        '3': 'March',
        '4': 'April',
        '5': 'May',
        '6': 'June',
        '7': 'July',
        '8': 'August',
        '9': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December',
    }
    month = Month.objects.get(id=month_id)
    date = timezone.now()
    current_year, current_month, _ = str(date).split('-')
    current_month_name = month_dict[str(int(current_month))]
    today = Month.objects.get(month=current_month_name, year=current_year)
    try:
        previous_month = Month.objects.get(id=month_id - 1)
    except Exception:
        previous_month = Month.objects.get(id=month_id)
    try:
        next_month = Month.objects.get(id=month_id + 1)
    except Exception:
        next_month = Month.objects.get(id=month_id)

    print("list: ", tasks_in_months)

    context = {
        'employee': employee,
        'tasks_in_months': tasks_in_months,
        'months': months,
        'month': month,
        'previous_month': previous_month,
        'next_month': next_month,
        'today': today,
    }
    return render(request, 'employee_in_months.html', context)


def task_in_months_no_id(request, tsk_id):
    date = timezone.now()
    current_year, current_month, _ = str(date).split('-')
    month_dict = {
        '1': 'January',
        '2': 'February',
        '3': 'March',
        '4': 'April',
        '5': 'May',
        '6': 'June',
        '7': 'July',
        '8': 'August',
        '9': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December',
    }
    month_name = month_dict[str(int(current_month))]
    month = Month.objects.get(month=month_name, year=current_year)
    return redirect('/task_in_months/{}/{}'.format(tsk_id, month.id))


def task_in_months(request, tsk_id, month_id):
    month_dict = {
        '1': 'January',
        '2': 'February',
        '3': 'March',
        '4': 'April',
        '5': 'May',
        '6': 'June',
        '7': 'July',
        '8': 'August',
        '9': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December',
    }
    if request.method == "POST":
        start = request.POST.get('start_month')
        try:
            start_year, start_month = str(start).split('-')
        except ValueError:
            return redirect('/task_in_months/{}/{}'.format(tsk_id, month_id))
        for month_obj in Month.objects.all():
            if month_obj.month == month_dict[str(int(start_month))] and month_obj.year == start_year:
                month_id = month_obj.id
                return redirect('/task_in_months/{}/{}'.format(tsk_id, month_id))
        return redirect('/task_in_months/{}/{}'.format(tsk_id, month_id))

    # data for one employee
    task = Project.objects.get(id=tsk_id)
    months = Month.objects.all()
    emps_in_months = []

    for employee in Employee.objects.all():
        employee_info = [employee]
        assignments = []
        # iterate through all months
        for counter, month in enumerate(Month.objects.all()):
            assignments.append('-')
            for assignment_per_months in AssignmentPerMonth.objects.all():  # set assignment_percentages to right month
                if employee.id == assignment_per_months.employee.id and task.id == assignment_per_months.task.id and month == assignment_per_months.month:
                    assignments[counter] = int(round(assignment_per_months.percentage, 2) * 100)
        employee_info.append(assignments[month_id - 1:month_id + 11])
        emps_in_months.append(employee_info)
    months = months[month_id - 1:month_id + 11]

    month_dict = {
        '1': 'January',
        '2': 'February',
        '3': 'March',
        '4': 'April',
        '5': 'May',
        '6': 'June',
        '7': 'July',
        '8': 'August',
        '9': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December',
    }
    month = Month.objects.get(id=month_id)
    date = timezone.now()
    current_year, current_month, _ = str(date).split('-')
    current_month_name = month_dict[str(int(current_month))]
    today = Month.objects.get(month=current_month_name, year=current_year)
    try:
        previous_month = Month.objects.get(id=month_id - 1)
    except Exception:
        previous_month = Month.objects.get(id=month_id)
    try:
        next_month = Month.objects.get(id=month_id + 1)
    except Exception:
        next_month = Month.objects.get(id=month_id)

    context = {
        'task': task,
        'emps_in_months': emps_in_months,
        'months': months,
        'month': month,
        'previous_month': previous_month,
        'next_month': next_month,
        'today': today,
    }
    return render(request, 'task_in_months.html', context)


# TIMESHEETS
def employee_time_no_id(request):
    date = timezone.now()
    current_year, current_month, _ = str(date).split('-')
    month_dict = {
        '1': 'January',
        '2': 'February',
        '3': 'March',
        '4': 'April',
        '5': 'May',
        '6': 'June',
        '7': 'July',
        '8': 'August',
        '9': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December',
    }
    month_name = month_dict[str(int(current_month))]
    month = Month.objects.get(month=month_name, year=current_year)
    return redirect('/employee_time/{}'.format(month.id))


def employee_time(request, id):
    employees = Employee.objects.all()
    assignments_per_month = AssignmentPerMonth.objects.all()
    months = Month.objects.all()
    assignments_sums = []

    month_dict = {
        '1': 'January',
        '2': 'February',
        '3': 'March',
        '4': 'April',
        '5': 'May',
        '6': 'June',
        '7': 'July',
        '8': 'August',
        '9': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December',
    }
    if request.method == "POST":
        start = request.POST.get('start_month')
        try:
            start_year, start_month = str(start).split('-')
        except ValueError:
            return redirect('/employee_time/{}'.format(id))
        for month_obj in Month.objects.all():
            if month_obj.month == month_dict[str(int(start_month))] and month_obj.year == start_year:
                month_id = month_obj.id
                return redirect('/employee_time/{}'.format(month_id))
        return redirect('/employee_time/{}'.format(id))

    # create list of lists with task sums for employees
    for employee in employees:
        tasks_sum = []
        # loop through months
        for month in months:
            sum = 0
            # if current month and employee in assignments are right sum the percentages
            for assignment_per_month in assignments_per_month:
                if assignment_per_month.employee == employee and assignment_per_month.month == month:
                    sum += assignment_per_month.percentage
            # append the current sum value to list
            tasks_sum.append(int(round(sum, 2) * 100))
        # Slice list to only have 12 entries
        tasks_sum = tasks_sum[(id - 1):(id + 11)]
        # append list to other lists
        assignments_sums.append(tasks_sum)

    months = months[(id - 1):(id + 11)]

    date = timezone.now()
    current_year, current_month, _ = str(date).split('-')
    current_month_name = month_dict[str(int(current_month))]
    today = Month.objects.get(month=current_month_name, year=current_year)
    previous_month = Month.objects.get(id=id - 1)
    next_month = Month.objects.get(id=id + 1)
    month = Month.objects.get(id=id)
    context = {
        'months': months,
        'assignments': assignments_sums,
        'employees': employees,
        'today': today,
        'previous_month': previous_month,
        'next_month': next_month,
        'month': month
    }
    return render(request, 'employee_time.html', context)


def task_time_no_id(request):
    date = timezone.now()
    current_year, current_month, _ = str(date).split('-')
    month_dict = {
        '1': 'January',
        '2': 'February',
        '3': 'March',
        '4': 'April',
        '5': 'May',
        '6': 'June',
        '7': 'July',
        '8': 'August',
        '9': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December',
    }
    month_name = month_dict[str(int(current_month))]
    month = Month.objects.get(month=month_name, year=current_year)
    return redirect('/task_time/{}'.format(month.id))


def task_time(request, id):
    tasks = Task.objects.all()
    assignments_per_month = AssignmentPerMonth.objects.all()
    months = Month.objects.all()
    assignment_sums = []

    month_dict = {
        '1': 'January',
        '2': 'February',
        '3': 'March',
        '4': 'April',
        '5': 'May',
        '6': 'June',
        '7': 'July',
        '8': 'August',
        '9': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December',
    }
    if request.method == "POST":
        start = request.POST.get('start_month')
        try:
            start_year, start_month = str(start).split('-')
        except ValueError:
            return redirect('/task_time/{}'.format(id))
        for month_obj in Month.objects.all():
            if month_obj.month == month_dict[str(int(start_month))] and month_obj.year == start_year:
                month_id = month_obj.id
                return redirect('/task_time/{}'.format(month_id))
        return redirect('/task_time/{}'.format(id))

    for task in tasks:
        employees_sum = []
        for month in months:
            sum = 0
            for assignment_per_month in assignments_per_month:
                if assignment_per_month.task.id == task.id and assignment_per_month.month == month:
                    sum += int(round(assignment_per_month.percentage, 2) * 100)
            employees_sum.append(sum)
        employees_sum = employees_sum[(id - 1):(id + 11)]
        assignment_sums.append(employees_sum)
    months = months[(id - 1):(id + 11)]

    date = timezone.now()
    current_year, current_month, _ = str(date).split('-')
    current_month_name = month_dict[str(int(current_month))]
    today = Month.objects.get(month=current_month_name, year=current_year)
    previous_month = Month.objects.get(id=id - 1)
    next_month = Month.objects.get(id=id + 1)
    month = Month.objects.get(id=id)
    context = {
        'months': months,
        'assignments': assignment_sums,
        'tasks': tasks,
        'today': today,
        'previous_month': previous_month,
        'next_month': next_month,
        'month': month,
    }
    return render(request, 'task_time.html', context)


# ADD NEW OBJECTS
def add_new_emp(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)

        # duplicates
        employee_firstname = form.data['firstname']
        employee_lastname = form.data['lastname']
        for employee in Employee.objects.all():
            if employee.firstname == employee_firstname and employee.lastname == employee_lastname:
                messages.error(request, "Employee already exists.")
                return redirect('/add_new_emp')
        if form.is_valid():
            # Restrictions
            date_format = "%Y-%m-%d"
            if datetime.date(datetime.strptime(form.data['hiring_date'], date_format)) > \
                    datetime.date(datetime.strptime(form.data['expiration_date'], date_format)):
                messages.error(request, "The Employees contract expires before he got hired")
                return redirect('/add_new_ass')

            form.save()
            return redirect('/data')
    else:
        form = EmployeeForm()
    context = {
        'form': form
    }
    return render(request, 'add_new_emp.html', context)


def add_new_proj(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        for project in Project.objects.all():
            if project.title == form.data['title']:
                messages.error(request, "The Project " + form.data['title'] + " already exists")
                return redirect('/add_new_proj')
        if form.is_valid():
            # Restrictions
            date_format = "%Y-%m-%d"
            if datetime.date(datetime.strptime(form.data['begin'], date_format)) > \
                    datetime.date(datetime.strptime(form.data['end'], date_format)):
                messages.error(request, "The Project ends before it started")
                return redirect('/add_new_proj')

            form.save()
            return redirect('/data')
    else:
        form = ProjectForm()
    context = {
        'form': form
    }
    return render(request, 'add_new_proj.html', context)


def add_new_pos(request):
    if request.method == "POST":
        form = PositionForm(request.POST)

        for position in Position.objects.all():
            if position.title == form.data['title']:
                messages.error(request, "The Position " + form.data['title'] + " already exists")
                return redirect('/add_new_pos')
        if form.is_valid():
            form.save()
            return redirect('/data')
    else:
        form = PositionForm()
    context = {
        'form': form
    }
    return render(request, 'add_new_pos.html', context)


def add_new_chair(request):
    if request.method == "POST":
        form = ChairForm(request.POST)
        for chair in Chair.objects.all():
            if chair.title == form.data['title']:
                messages.error(request, "The Chair " + form.data['title'] + " already exists")
                return redirect('/add_new_chair')

        if form.is_valid():
            form.save()
            return redirect('/data')
    else:
        form = ChairForm()
    context = {
        'form': form
    }
    return render(request, 'add_new_chair.html', context)


def add_new_ass(request):
    months = Month.objects.all()
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            emp = Employee.objects.get(id=form.data['employee'])
            tsk = Task.objects.get(id=form.data['task'])
            date_format = "%Y-%m-%d"
            if datetime.date(datetime.strptime(form.data['end'], date_format)) > emp.expiration_date:
                messages.error(request, "The Employees contract ends before the assignment ends")
                return redirect('/add_new_ass')
            # Only check this constraint for projects
            try:
                project = Project.objects.get(id=form.data['task'])
                if datetime.date(datetime.strptime(form.data['end'], date_format)) > project.end:
                    messages.error(request, "The Project ends before the assignment ends")
                    return redirect('/add_new_ass')
            except Project.DoesNotExist:
                print('Task is not a project')

            if datetime.date(datetime.strptime(form.data['start'], date_format)) > \
                    datetime.date(datetime.strptime(form.data['end'], date_format)):
                messages.error(request, "The Assignment ends before it even started")
                return redirect('/add_new_ass')
            # CHECK FOR POSITION <= 100%
            # Get id's of all postions
            postions = Position.objects.all()
            postion_ids = []
            for position in postions:
                postion_ids.append(position.id)
            # check if selected id is present in postion_ids list
            if int(form.data['task']) in postion_ids:
                sum = 0
                # sum all percentages for this position
                for assignment in Assignment.objects.all():
                    if assignment.task.id == int(form.data['task']):
                        sum = sum + assignment.percentage
                # check if new assignment would overbook position
                if sum + float(form.data['percentage']) > 1:
                    messages.error(request,
                                   "This assignment would overbook Chair Postion( Title: " + Position.objects.get(
                                       id=int(form.data['task'])).title + ").")
                    return redirect('/add_new_ass')
            # CHECK IF CHAIR ISNT OVERBOOKED
            chairs = Chair.objects.all()
            chair_ids = []
            for chair in chairs:
                chair_ids.append(chair.id)
            # count assignments to current chair
            if int(form.data['task']) in chair_ids:
                sum = 0
                for assignment in Assignment.objects.all():
                    if assignment.task.id == int(form.data['task']):
                        sum = sum + assignment.percentage
                # check if count equal to requirement of current chair, if true dont allow assign
                if float(form.data['percentage']) + sum > Chair.objects.get(id=int(form.data['task'])).requirement:
                    messages.error(request, "Chair " + Chair.objects.get(
                        id=int(form.data['task'])).title + " would be overbooked.")
                    return redirect('/add_new_ass')

            # Get Information about the dates and calculate the duration
            emp = Employee.objects.get(id=form.data['employee'])
            task = Task.objects.get(id=form.data['task'])
            month_dict = {
                '1': 'January',
                '2': 'February',
                '3': 'March',
                '4': 'April',
                '5': 'May',
                '6': 'June',
                '7': 'July',
                '8': 'August',
                '9': 'September',
                '10': 'October',
                '11': 'November',
                '12': 'December',
            }
            start_year, start_month, start_day = str(form.data['start']).split('-')
            end_year, end_month, end_day = str(form.data['end']).split('-')
            year_delta = int(end_year) - int(start_year)
            month_delta = int(end_month) - int(start_month)
            duration = 0
            if year_delta >= 0:
                duration += year_delta * 12 + month_delta
            # Use information to initialize AssignmentPerMonth Objects
            # as long as duration of Assignment is greater than zero
            first = True
            while duration >= 0:
                start_month = int(start_month)
                start_year = int(start_year)
                month_name = month_dict[str(start_month)]
                month_obj = Month.objects.get(month=month_name, year=start_year)
                # Create AssignmentPerMonth Object
                responsibility = form.data['responsibility']
                if responsibility == 'true':
                    responsibility = True
                else:
                    responsibility = False

                percentage = form.data['percentage']
                # The assignments percentage in the first and last month further depends on the day
                if first:
                    percentage = float(percentage) * ((31 - float(start_day)) / 30.0)
                if duration == 0:
                    percentage = float(percentage) * (float(end_day) / 30.0)

                assignment_per_month = AssignmentPerMonth(employee=emp, task=task, month=month_obj, duration=duration,
                                                          percentage=percentage,
                                                          responsibility=responsibility)
                assignment_per_month.save()

                # Increase the month and decrease the Assignments duration by one
                if start_month < 12:
                    start_month += 1
                else:
                    start_month = 1
                    start_year += 1
                duration -= 1
                first = False

            form.save()
            return redirect('/data')
    else:
        form = AssignmentForm()

    context = {
        'form': form
    }
    return render(request, 'add_new_ass.html', context)


# EDIT OBJECTS
def edit_emp(request, id):
    employee = Employee.objects.get(id=id)
    context = {
        'employee': employee
    }
    return render(request, 'edit_emp.html', context)


def edit_task(request, id):
    projects = Project.objects.all()
    positions = Position.objects.all()
    chairs = Chair.objects.all()

    for project in projects:
        if project.id == id:
            return redirect('/edit_proj/{}'.format(id))
    for position in positions:
        if position.id == id:
            return redirect('/edit_pos/{}'.format(id))
    for chair in chairs:
        if chair.id == id:
            return redirect('/edit_chair/{}'.format(id))

    return redirect('/data')


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


# UPDATE OBJECTS
def update_emp(request, id):
    employee = Employee.objects.get(id=id)
    form = EmployeeForm(request.POST, instance=employee)
    if form.is_valid():
        form.save()
        return redirect('/data')
    context = {
        'employee': employee
    }
    return render(request, 'edit_emp.html', context)


def update_proj(request, id):
    project = Project.objects.get(id=id)
    form = ProjectForm(request.POST, instance=project)
    if form.is_valid():
        form.save()
        return redirect('/data')
    context = {
        'project': project
    }
    return render(request, 'edit_proj.html', context)


def update_pos(request, id):
    position = Position.objects.get(id=id)
    form = PositionForm(request.POST, instance=position)
    if form.is_valid():
        form.save()
        return redirect('/data')
    context = {
        'position': position
    }
    return render(request, 'edit_pos.html', context)


def update_chair(request, id):
    chair = Chair.objects.get(id=id)
    form = ChairForm(request.POST, instance=chair)
    if form.is_valid():
        form.save()
        return redirect('/data')
    context = {
        'chair': chair
    }
    return render(request, 'edit_chair.html', context)


def update_ass(request, id):
    assignment = Assignment.objects.get(id=id)
    percentage_old = assignment.percentage
    responsibility_old = assignment.responsibility
    start_old = assignment.start
    end_old = assignment.end
    comment_old = assignment.comment

    form = EditAssignmentForm(request.POST, instance=assignment)
    if form.is_valid():

        # GET FORM DATA
        emp = Employee.objects.filter(id=assignment.employee.id).first()
        task = Task.objects.filter(id=assignment.task.id).first()
        percentage = form.data['percentage']
        try:
            responsibility = form.data['responsibility']
        except Exception:
            responsibility = False
        comment = form.data['comment']
        start = form.data['start']
        end = form.data['end']

        # RESTRICTION: USER SHALL NOT BE ABLE TO EDIT PAST ASSIGNMENTS
        date_format = "%Y-%m-%d"
        if datetime.strptime(start, date_format).date() < datetime.today().date():
            messages.error(request, "Cannot update Assignments in past months.")
            return redirect('/edit_ass/{}'.format(id))

        # CREATE A NEW ASSIGNMENT BEFORE AND AFTER THE NEWLY SET TIMEFRAME start_old -> start    and    end -> end_old
        # Before: start_old -> start
        ass_before = Assignment(employee=emp, task=task, start=start_old, end=start,
                                percentage=percentage_old, responsibility=responsibility_old,
                                comment=comment_old)
        ass_before.save()
        # After: end -> end_old
        ass_after = Assignment(employee=emp, task=task, start=end, end=end_old,
                               percentage=percentage_old, responsibility=responsibility_old,
                               comment=comment_old)
        ass_after.save()

        # UPDATE ASSIGNMENTPERMONTHS WITHIN THE NEWLY SET TIMEFRAME
        # GET INFORMATION ABOUT THE NEW TIMEFRAMES
        month_dict = {
            '1': 'January',
            '2': 'February',
            '3': 'March',
            '4': 'April',
            '5': 'May',
            '6': 'June',
            '7': 'July',
            '8': 'August',
            '9': 'September',
            '10': 'October',
            '11': 'November',
            '12': 'December',
        }
        print(form.data)
        start_year, start_month, start_day = str(form.data['start']).split('-')
        end_year, end_month, end_day = str(form.data['end']).split('-')
        end_year_update, end_month_update, end_day_update = str(form.data['end']).split('-')
        print('-----Update-----')
        # start -> end
        # Calculate duration of changes
        print('Start:', start_year, start_month)
        print('End:', end_year_update, end_month_update)
        year_delta = int(end_year_update) - int(start_year)
        print('Year delta:', year_delta)
        month_delta = int(end_month_update) - int(start_month)
        print('Month delta', month_delta)
        duration = 0
        if year_delta >= 0:
            duration += year_delta * 12 + month_delta
        # Use information to edit AssignmentPerMonth Objects
        first = True
        while duration >= 0:
            print('Duration:', duration)
            start_year = int(start_year)
            start_month = int(start_month)
            month_name = month_dict[str(start_month)]
            month_obj = Month.objects.get(month=month_name, year=start_year)
            print('Month:', month_obj)
            # Edit AssignmentPerMonth Object
            try:
                ass = AssignmentPerMonth.objects.get(employee=emp, task=task, month=month_obj)
            # Create new AssignmentPerMonth Object if it does not yet exist
            except AssignmentPerMonth.DoesNotExist:
                ass = AssignmentPerMonth(employee=emp, task=task, month=month_obj, duration=duration)
            print('Assignment:', ass)
            ass.percentage = float(percentage)
            if first:
                ass.percentage = float(percentage) * ((31.0 - float(start_day)) / 30.0)
            if duration == 0:
                ass.percentage = float(percentage) * (float(end_day) / 30.0)

            ass.responsibility = responsibility
            ass.save()
            # Iterator while loop
            if start_month < 12:
                start_month += 1
            else:
                start_month = 1
                start_year += 1
            duration -= 1
            first = False

        form.save()
        return redirect('/data')
    context = {
        'assignment': assignment
    }
    return render(request, 'edit_ass.html', context)


# DELETE OBJECTS
def delete_emp(request, id):
    employee = Employee.objects.get(id=id)
    employee.delete()
    return redirect('/data')


def delete_proj(request, id):
    project = Project.objects.get(id=id)
    project.delete()
    return redirect('/data')


def delete_pos(request, id):
    position = Position.objects.get(id=id)
    position.delete()
    return redirect('/data')


def delete_chair(request, id):
    chair = Chair.objects.get(id=id)
    chair.delete()
    return redirect('/data')


def delete_ass(request, id):
    assignment = Assignment.objects.get(id=id)

    month_dict = {
        '1': 'January',
        '2': 'February',
        '3': 'March',
        '4': 'April',
        '5': 'May',
        '6': 'June',
        '7': 'July',
        '8': 'August',
        '9': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December',
    }
    start = assignment.start
    end = assignment.end
    start_year, start_month, _ = str(start).split('-')
    end_year, end_month, _ = str(end).split('-')
    year_delta = int(end_year) - int(start_year)
    month_delta = int(end_month) - int(start_month)
    duration = 0
    if year_delta >= 0:
        duration += year_delta * 12 + month_delta

    while duration > 0:
        start_month = int(start_month)
        month_name = month_dict[str(start_month)]
        month_obj = Month.objects.get(month=month_name, year=start_year)
        # Create AssignmentPerMonth Object
        assignment_per_month = AssignmentPerMonth.objects.get(employee=assignment.employee, task=assignment.task,
                                                              month=month_obj)
        assignment_per_month.delete()

        # Increase the month and decrease the Assignments duration by one
        if start_month < 12:
            start_month += 1
        else:
            start_month = 1
            start_year += 1
        duration -= 1

    assignment.delete()
    return redirect('/data')
