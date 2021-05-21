from datetime import datetime

from django.shortcuts import render, redirect
from django.utils import timezone
from erpapp.forms import EmployeeForm, ProjectForm, PositionForm, ChairForm, AssignmentForm, EditAssignmentForm
from django.contrib import messages
from erpapp.models import Employee, Project, Position, Chair, Assignment, Task, Month, AssignmentPerMonth


# CRUD DATA (CREATE/READ/UPDATE/DELETE)
def data(request):
    # Retrieve object data
    employees = Employee.objects.all()
    projects = Project.objects.all()
    positions = Position.objects.all()
    chairs = Chair.objects.all()
    tasks = Task.objects.all()
    assignments = Assignment.objects.all()

    # Collect information about the projects and employees to throw warning messages
    # when ressources/capacity is overused
    project_infos = []  # Information about the projects
    employee_infos = []  # Information about the employees
    # Get Assignments for current month
    date = timezone.now()
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
    current_year, current_month, _ = str(date).split('-')
    month_name = month_dict[str(int(current_month))]
    month_object = Month.objects.get(year=current_year, month=month_name)
    assignmentpermonths = AssignmentPerMonth.objects.all().filter(month=month_object)
    # Collect Projects Information
    # (project_sum, available ressources, project title, difference between sum and ressources)
    for project in projects:
        sum = 0
        ressources = project.ressources
        title = project.title
        # Calculate the sum by checking all assignments in current month
        for assignment in assignmentpermonths:
            if assignment.task.id == project.id:
                sum += assignment.percentage
        # By what amount the project is currently overbooked
        diff = int(round((sum - ressources), 2) * 100)
        project_infos.append((sum, ressources, title, diff))  # Append information to list

    # Collect Employees Information
    # (Employee, summed assignment percentages, max Capacity and the difference between them)
    for employee in employees:
        employee_sum = 0
        # Calculate the sum by checking all assignments in current month
        for task in tasks:
            # Calculate the sum by checking all assignments in current month
            for assignment in assignmentpermonths:
                if assignment.task.id == task.id and assignment.employee.id == employee.id:
                    employee_sum += assignment.percentage
        # By what amount the employee is currently overbooked
        overload = int(round((employee_sum - employee.capacity), 2) * 100)
        employee_infos.append((employee, employee_sum, employee.capacity, overload))  # Append information to list

    # Create a list of warning messages,
    # if the sum of assignment percentages is greater than the max available ressources/capacity
    warnings = []
    for project_info in project_infos:
        if project_info[0] > project_info[1]:
            warnings.append('{} is currently using too many ressources! ({}%)'.format(project_info[2], project_info[3]))
    for employee_info in employee_infos:
        if employee_info[1] > employee_info[2]:
            warnings.append('{} is currently working too many hours! ({}%)'.format(employee_info[0], employee_info[3]))
    warnings_length = len(warnings)

    # Provide information for frontend
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
        'month_object': month_object,
    }
    return render(request, 'data.html', context)


# DASHBOARD / INDEX / HOME
def dashboard_no_id(request):
    # Redirecting to current month if no month was submitted
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

    # Frontend month selector
    if request.method == "POST":
        # Get the chosen month
        start = request.POST.get('start_month')
        # Try to extract month and year of selected date
        try:
            start_year, start_month = str(start).split('-')
        # Redirect to current month if no date was selected
        except ValueError:
            return redirect('/dashboard/')
        # Check if selected month exists
        for month_obj in Month.objects.all():
            # Redirect to selected month if yes
            if month_obj.month == month_dict[str(int(start_month))] and month_obj.year == start_year:
                month_id = month_obj.id
                return redirect('/dashboard/{}'.format(month_id))
        # Redirect to current month otherwise
        return redirect('/dashboard/')

    # Get previous and following/next month information for frontend date switcher
    date = timezone.now()
    current_year, current_month, _ = str(date).split('-')
    current_month_name = month_dict[str(int(current_month))]
    today = Month.objects.get(month=current_month_name, year=current_year)
    try:
        previous_month = Month.objects.get(id=id - 1)
    # redirect to last selected month if previous month does not exist
    except Exception:
        previous_month = Month.objects.get(id=id)
    try:
        next_month = Month.objects.get(id=id + 1)
    # redirect to last selected month if following/next month does not exist
    except Exception:
        next_month = Month.objects.get(id=id)

    # Collect information for each row in the data table (employee)
    # [[[employee, sum, capacity, workload], [project_percentages, ...], [position_percentages, ...], [chair_percentages, ...]],
    #  [[employee, sum, capacity, workload], [project_percentages, ...], [position_percentages, ...], [chair_percentages, ...]],
    #  [[employee, sum, capacity, workload], [project_percentages, ...], [position_percentages, ...], [chair_percentages, ...]],
    #  ...
    # ]
    employee_rows = []
    for employee in Employee.objects.all():
        # Collect information for each employee and append it to the matrix (employee_rows)
        employee_sum = 0
        # look through all assignments for all tasks for one employee
        # preselect assignments_per_months for selected month
        assignments_per_months_for_month = AssignmentPerMonth.objects.filter(month=month)
        for task in tasks:
            for assignment_per_month in assignments_per_months_for_month:
                # if assignment in month exists add percentage to sum
                if employee.id == assignment_per_month.employee.id and task.id == assignment_per_month.task.id:
                    employee_sum = employee_sum + assignment_per_month.percentage
        # get capacity and calculate workload
        employee_capacity = employee.capacity
        employee_worklooad = employee_sum / employee_capacity

        # attach these infos to first element in list for each employee
        employee_title = [(employee, int(employee_sum * 100), int(employee_capacity * 100), employee_worklooad)]

        # COLLECT ASSIGNMENT PERCENTAGES AND RESPONSIBILITY FOR EACH PROJECT, CHAIR POSITION AND CHAIR TASK
        # PROJECT
        assignment_infos_project = []
        for counter, project in enumerate(Project.objects.all()):
            # Fill the list
            assignment_infos_project.append(['-', False])
            # Set new values if assignment exists
            for assignment_per_month in assignments_per_months_for_month:
                if employee.id == assignment_per_month.employee.id and project.id == assignment_per_month.task.id:
                    assignment_infos_project[counter] = [int(assignment_per_month.percentage * 100),
                                                         assignment_per_month.responsibility]
        # append to row for current employee
        employee_title.append(assignment_infos_project)

        # CHAIR POSITION
        assignment_infos_position = []
        for counter, position in enumerate(Position.objects.all()):
            # Fill the list
            assignment_infos_position.append(['-', False])
            # Set new values if assignment exists
            for assignment_per_month in assignments_per_months_for_month:
                if employee.id == assignment_per_month.employee.id and position.id == assignment_per_month.task.id:
                    assignment_infos_position[counter] = [int(assignment_per_month.percentage * 100),
                                                          assignment_per_month.responsibility]
        # append to row for current employee
        employee_title.append(assignment_infos_position)

        # CHAIR TASK
        assignment_infos_chair = []
        for counter, chair in enumerate(Chair.objects.all()):
            # Fill the list
            assignment_infos_chair.append(['-', False])
            # Set new values if assignment exists
            for assignment_per_month in assignments_per_months_for_month:
                if employee.id == assignment_per_month.employee.id and chair.id == assignment_per_month.task.id:
                    assignment_infos_chair[counter] = [int(assignment_per_month.percentage * 100),
                                                       assignment_per_month.responsibility]
        # append to row for current employee
        employee_title.append(assignment_infos_chair)
        # append row to matrix
        employee_rows.append(employee_title)
    # print("employee_rows:, ", employee_rows)

    # Create a list for each task (projects, chair positions, chair tasks)
    # that contains information about the summed up assignment's percentages and the available ressources
    task_sums = []
    for project in Project.objects.all():
        sum = 0
        for assignment_per_month in assignments_per_months_for_month:
            if project.id == assignment_per_month.task.id:
                sum = sum + assignment_per_month.percentage
        task_sums.append([int(sum * 100), int(project.ressources * 100)])
    for position in Position.objects.all():
        sum = 0
        for assignment_per_month in assignments_per_months_for_month:
            if position.id == assignment_per_month.task.id:
                sum = sum + assignment_per_month.percentage
        task_sums.append([int(sum * 100), int(position.ressources * 100)])
    for chair in Chair.objects.all():
        sum = 0
        for assignment_per_month in assignments_per_months_for_month:
            if chair.id == assignment_per_month.task.id:
                sum = sum + assignment_per_month.percentage
        task_sums.append([int(sum * 100), int(chair.requirement * 100)])
    # print("task_sums: ", task_sums)

    # GET INFORMARTION FOR ALL TASKS (Projects, Chair Positions, Chair Tasks)
    # (used in the table header)
    task_infos = []
    for project in Project.objects.all():
        sum = 0
        for assignment_per_month in assignments_per_months_for_month:
            if project.id == assignment_per_month.task.id:
                sum = sum + assignment_per_month.percentage
        task_workload = sum / project.ressources
        task_infos.append([project, int(sum * 100), int(project.ressources * 100), round(task_workload, 2)])
    # print("projects: ", task_infos)
    for position in Position.objects.all():
        sum = 0
        for assignment_per_month in assignments_per_months_for_month:
            if position.id == assignment_per_month.task.id:
                sum = sum + assignment_per_month.percentage
        task_workload = sum / position.ressources
        task_infos.append([position, int(sum * 100), int(position.ressources * 100), round(task_workload, 2)])
    # print("postions: ", task_infos)
    for chair in Chair.objects.all():
        sum = 0
        for assignment_per_month in assignments_per_months_for_month:
            if chair.id == assignment_per_month.task.id:
                sum = sum + assignment_per_month.percentage
        chair_workload = sum / chair.requirement
        task_infos.append([chair, int(sum * 100), int(chair.requirement * 100), round(chair_workload, 2)])
    # print("chairs:,", task_infos)

    context = {
        'tasks': tasks,
        'task_infos': task_infos,
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
    # Redirecting to current month if no month was submitted
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
    # Frontend month selector
    if request.method == "POST":
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
        # Get the chosen month
        start = request.POST.get('start_month')
        # Try to extract month and year of selected date
        try:
            start_year, start_month = str(start).split('-')
        # Redirect to current month if no date was selected
        except ValueError:
            return redirect('/employee_in_months/{}/{}'.format(emp_id, month_id))
        # Check if selected month exists
        for month_obj in Month.objects.all():
            # Redirect to selected month if yes
            if month_obj.month == month_dict[str(int(start_month))] and month_obj.year == start_year:
                month_id = month_obj.id
                return redirect('/employee_in_months/{}/{}'.format(emp_id, month_id))
        # Redirect to current month otherwise
        return redirect('/employee_in_months/{}/{}'.format(emp_id, month_id))
    # Get previous and following/next month information for frontend date switcher
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
    # redirect to last selected month if previous month does not exist
    except Exception:
        previous_month = Month.objects.get(id=month_id)
    try:
        next_month = Month.objects.get(id=month_id + 1)
    # redirect to last selected month if following/next month does not exist
    except Exception:
        next_month = Month.objects.get(id=month_id)

    # Collect assignment data for selected employee
    employee = Employee.objects.get(id=emp_id)
    # preselect assignments_for_months for selected employee
    assignments_per_month_for_employee = AssignmentPerMonth.objects.filter(employee=employee)
    # Table body matrix
    tasks_in_months = []
    for task in Task.objects.all():
        # Task title as first element of row
        task_info = [task.title]
        # Percentages in each month
        assignments_percentages = []
        # Will be set true, if at least one assignment in the following 12 months exists
        append = False
        # Loop through the next 12 months starting at selected date
        for idx, month in enumerate(Month.objects.all()[month_id - 1:month_id + 11]):
            # Fill the list
            assignments_percentages.append('-')
            for assignment_per_months in assignments_per_month_for_employee:
                if task.id == assignment_per_months.task.id and assignment_per_months.month == month:
                    assignments_percentages[idx] = int(round(assignment_per_months.percentage, 2) * 100)
                    append = True
        if append:
            task_info.append(assignments_percentages)
            tasks_in_months.append(task_info)
    # print("list: ", tasks_in_months)
    context = {
        'employee': employee,
        'tasks_in_months': tasks_in_months,
        'months': Month.objects.all()[month_id - 1:month_id + 11],
        'month': month,
        'previous_month': previous_month,
        'next_month': next_month,
        'today': today,
    }
    return render(request, 'employee_in_months.html', context)


def task_in_months_no_id(request, tsk_id):
    # Redirecting to current month if no month was submitted
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
        # Get the chosen month
        start = request.POST.get('start_month')
        # Try to extract month and year of selected date
        try:
            start_year, start_month = str(start).split('-')
        # Redirect to current month if no date was selected
        except ValueError:
            return redirect('/task_in_months/{}/{}'.format(tsk_id, month_id))
        # Check if selected month exists
        for month_obj in Month.objects.all():
            # Redirect to selected month if yes
            if month_obj.month == month_dict[str(int(start_month))] and month_obj.year == start_year:
                month_id = month_obj.id
                return redirect('/task_in_months/{}/{}'.format(tsk_id, month_id))
        # Redirect to current month otherwise
        return redirect('/task_in_months/{}/{}'.format(tsk_id, month_id))
    # Get previous and following/next month information for frontend date switcher
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
    # redirect to last selected month if previous month does not exist
    except Exception:
        previous_month = Month.objects.get(id=month_id)
    try:
        next_month = Month.objects.get(id=month_id + 1)
    # redirect to last selected month if following/next month does not exist
    except Exception:
        next_month = Month.objects.get(id=month_id)

    # Get selected task object
    task = Task.objects.get(id=tsk_id)
    # preselect assignments_for_months for selected task
    assignments_for_months_for_task = AssignmentPerMonth.objects.filter(task=task)
    # Collect data for table body
    emps_in_months = []
    for employee in Employee.objects.all():
        # Take employee as first value
        employee_info = [employee]
        # List with percentages of each Employee assigned to this task
        assignments_percentage = []
        # Will later be set to true if any assignment exists in the next 12 months starting at selected date
        append = False
        for counter, month in enumerate(Month.objects.all()[month_id - 1: month_id + 11]):
            # Fill the list
            assignments_percentage.append('-')
            # Search for assignments
            for assignment_per_months in assignments_for_months_for_task:
                if employee.id == assignment_per_months.employee.id and assignment_per_months.month == month:
                    assignments_percentage[counter] = int(round(assignment_per_months.percentage, 2) * 100)
                    append = True
        if append:
            employee_info.append(assignments_percentage)
            emps_in_months.append(employee_info)

    context = {
        'task': task,
        'emps_in_months': emps_in_months,
        'months': Month.objects.all()[month_id - 1: month_id + 11],
        'month': month,
        'previous_month': previous_month,
        'next_month': next_month,
        'today': today,
    }
    return render(request, 'task_in_months.html', context)


# TIMESHEETS
def employee_time_no_id(request):
    # Redirecting to current month if no month was submitted
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
    employees = []
    assignments_per_month = AssignmentPerMonth.objects.all()
    months_sliced = Month.objects.all()[(id - 1):(id + 11)]
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
    # Frontend month selector
    if request.method == "POST":
        # Get selected month
        start = request.POST.get('start_month')
        try:
            start_year, start_month = str(start).split('-')
        # Reload page of no month was selected
        except ValueError:
            return redirect('/employee_time/{}'.format(id))
        # Redirect to newly set month
        for month_obj in Month.objects.all():
            if month_obj.month == month_dict[str(int(start_month))] and month_obj.year == start_year:
                month_id = month_obj.id
                return redirect('/employee_time/{}'.format(month_id))
        # Reload page if month does not exist
        return redirect('/employee_time/{}'.format(id))

    # Create matrix with summed up percentages for each month and selected employee
    for employee in Employee.objects.all():
        tasks_sum = []
        # Will late be set to True if any assignment exists in selected timeframe
        append = False
        for month in months_sliced:
            sum = 0
            for assignment_per_month in assignments_per_month:
                if assignment_per_month.employee == employee and assignment_per_month.month == month:
                    sum += assignment_per_month.percentage
                    append = True
            # append the current sum value to list
            tasks_sum.append(int(round(sum, 2) * 100))

        # append row to matrix if not empty
        if append:
            assignments_sums.append(tasks_sum)
            employees.append(employee)

    # Get previous and following/next month for frontend month switcher
    date = timezone.now()
    current_year, current_month, _ = str(date).split('-')
    current_month_name = month_dict[str(int(current_month))]
    today = Month.objects.get(month=current_month_name, year=current_year)
    previous_month = Month.objects.get(id=id - 1)
    next_month = Month.objects.get(id=id + 1)
    month = Month.objects.get(id=id)

    context = {
        'months': months_sliced,
        'assignments': assignments_sums,
        'employees': employees,
        'today': today,
        'previous_month': previous_month,
        'next_month': next_month,
        'month': month
    }
    return render(request, 'employee_time.html', context)


def task_time_no_id(request):
    # Redirecting to current month if no month was submitted
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
    tasks = []
    assignments_per_month = AssignmentPerMonth.objects.all()
    months_sliced = Month.objects.all()[(id - 1):(id + 11)]
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
    # Frontend month selector
    if request.method == "POST":
        # Get selected month
        start = request.POST.get('start_month')
        try:
            start_year, start_month = str(start).split('-')
        # Reload page of no month was selected
        except ValueError:
            return redirect('/task_time/{}'.format(id))
        # Redirect to newly set month
        for month_obj in Month.objects.all():
            if month_obj.month == month_dict[str(int(start_month))] and month_obj.year == start_year:
                month_id = month_obj.id
                return redirect('/task_time/{}'.format(month_id))
        # Reload page if month does not exist
        return redirect('/task_time/{}'.format(id))

    # Create matrix with summed up percentages for each month and selected task
    for task in Task.objects.all():
        employees_sum = []
        # Will later be set to True if any assignment exists in selected timeframe
        append = False
        for month in months_sliced:
            sum = 0
            for assignment_per_month in assignments_per_month:
                if assignment_per_month.task.id == task.id and assignment_per_month.month == month:
                    sum += int(round(assignment_per_month.percentage, 2) * 100)
                    append = True
            employees_sum.append(sum)
        # append row to matrix if not empty
        if append:
            assignment_sums.append(employees_sum)
            tasks.append(task)

    # Get previous and following/next month for frontend month switcher
    date = timezone.now()
    current_year, current_month, _ = str(date).split('-')
    current_month_name = month_dict[str(int(current_month))]
    today = Month.objects.get(month=current_month_name, year=current_year)
    previous_month = Month.objects.get(id=id - 1)
    next_month = Month.objects.get(id=id + 1)
    month = Month.objects.get(id=id)

    context = {
        'months': months_sliced,
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
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            emp = Employee.objects.get(id=form.data['employee'])
            task = Task.objects.get(id=form.data['task'])
            date_format = "%Y-%m-%d"
            # RESTRICTION: Employees contract shall not expire before assignment ends
            if datetime.date(datetime.strptime(form.data['end'], date_format)) > emp.expiration_date:
                messages.error(request, "The Employees contract ends before the assignment ends")
                return redirect('/add_new_ass')
            # RESTRICTION: Project shall not end before the assignment
            try:
                project = Project.objects.get(id=form.data['task'])
                if datetime.date(datetime.strptime(form.data['end'], date_format)) > project.end:
                    messages.error(request, "The Project ends before the assignment ends")
                    return redirect('/add_new_ass')
            except Project.DoesNotExist:
                print('Task is not a project')
            # RESTRICTION: Assignments end date must always be later than assignment start date
            if datetime.date(datetime.strptime(form.data['start'], date_format)) > \
                    datetime.date(datetime.strptime(form.data['end'], date_format)):
                messages.error(request, "The Assignment ends before it even started")
                return redirect('/add_new_ass')

            # RESTRICTION: Chair Position and Chair Task shall not use more ressources than available
            # Get id's of all positions
            positions = Position.objects.all()
            position_ids = []
            for position in positions:
                position_ids.append(position.id)
            # check if selected id is present in position_ids list
            if int(form.data['task']) in position_ids:
                sum = 0
                # sum all assignment's percentages for this position
                for assignment in Assignment.objects.all():
                    if assignment.task.id == int(form.data['task']):
                        sum = sum + assignment.percentage
                # check if new assignment would overbook position
                if sum + float(form.data['percentage']) > Position.objects.get(id=form.data['task']).ressources:
                    messages.error(request,
                                   "This assignment would overbook Postion( Title: " + Position.objects.get(
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

            # RESTRICTION: Assignments shall not overlap
            assignments = Assignment.objects.filter(employee=emp, task=task)
            for ass1 in assignments:
                ass1_start = ass1.start
                ass1_end = ass1.end
                ass2_start = datetime.strptime(form.data['start'], date_format).date()
                ass2_end = datetime.strptime(form.data['end'], date_format).date()
                if (ass2_start <= ass1_end <= ass2_end) or (ass2_start <= ass1_start <= ass2_end) or (ass2_start <= ass1_start and ass2_end >= ass1_end) or (ass1_start <= ass2_start and ass1_end >= ass2_end):
                    messages.error(request, "Assignment would overlap with other Assignment(s).")
                    return redirect('/add_new_ass')

            # CREATE ASSIGNMENTPERMONTH OBJECTS
            # Get Information about the dates and calculate the duration
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
            # as long as duration of Assignment is greater than or equal to zero
            first = True
            while duration >= 0:
                start_month = int(start_month)
                start_year = int(start_year)
                month_name = month_dict[str(start_month)]
                month_obj = Month.objects.get(month=month_name, year=start_year)

                responsibility = form.data['responsibility']
                if responsibility == 'true':
                    responsibility = True
                else:
                    responsibility = False
                percentage = form.data['percentage']
                # The first and last Months percentage needs to regard the day
                month_days = {
                    1: 31,
                    2: 28,
                    3: 31,
                    4: 30,
                    5: 31,
                    6: 30,
                    7: 31,
                    8: 31,
                    9: 30,
                    10: 31,
                    11: 30,
                    12: 31
                }
                if first:
                    percentage = float(percentage) * ((month_days[int(start_month)]+1 - float(start_day)) / month_days[int(start_month)])
                if duration == 0:
                    percentage = float(percentage) * (float(end_day) / month_days[int(start_month)])

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
    # Collect old object data
    percentage_old = assignment.percentage
    responsibility_old = assignment.responsibility
    start_old = assignment.start_formatted
    end_old = assignment.end_formatted
    comment_old = assignment.comment

    form = EditAssignmentForm(request.POST, instance=assignment)
    if form.is_valid():
        # convert strings to datetime.date objects to easily compare (-> restrictions)
        format = '%Y-%m-%d'
        start_old_date = datetime.strptime(start_old, format).date()
        start_new_date = datetime.strptime(assignment.start_formatted, format).date()
        end_old_date = datetime.strptime(end_old, format).date()
        end_new_date = datetime.strptime(assignment.end_formatted, format).date()

        # RESTRICTION: Start must be earlier than end
        if not (start_new_date < end_new_date):
            messages.error(request, "Start date must be earlier than end date.")
            return redirect('/edit_ass/{}'.format(id))

        # RESTRICTION: NEW TIMEFRAME MUST BE WITHIN ASSIGNMENT
        if not ((start_old_date <= start_new_date <= end_old_date)
                and (start_old_date <= end_new_date <= end_old_date)):
            messages.error(request, "Start and end date must be within the assignments timeframe.")
            return redirect('/edit_ass/{}'.format(id))

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

        # CREATE A NEW ASSIGNMENT WITH OLD VALUES BEFORE AND AFTER THE NEWLY SET TIMEFRAME
        # start_old -> start    and    end -> end_old
        # Before: start_old -> start
        if start_old != start:
            ass_before = Assignment(employee=emp, task=task, start=start_old, end=start,
                                    percentage=percentage_old, responsibility=responsibility_old,
                                    comment=comment_old)
            ass_before.save()
        # After: end -> end_old
        if end != end_old:
            ass_after = Assignment(employee=emp, task=task, start=end, end=end_old,
                                   percentage=percentage_old, responsibility=responsibility_old,
                                   comment=comment_old)
            ass_after.save()

        # UPDATE ASSIGNMENTPERMONTHS WITHIN THE NEW TIMEFRAME
        # get all the needed information about the dates
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
        end_year_update, end_month_update, end_day_update = str(form.data['end']).split('-')

        # Calculate AssignmentPerMonth count (duration = end - start)
        year_delta = int(end_year_update) - int(start_year)
        month_delta = int(end_month_update) - int(start_month)
        duration = 0
        if year_delta >= 0:
            duration += year_delta * 12 + month_delta

        # Use information to update AssignmentPerMonth Objects
        first = True
        while duration >= 0:
            # Convert the data
            start_year = int(start_year)
            start_month = int(start_month)
            month_name = month_dict[str(start_month)]
            month_obj = Month.objects.get(month=month_name, year=start_year)
            # Paste the data
            ass = AssignmentPerMonth.objects.get(employee=emp, task=task, month=month_obj)
            ass.percentage = float(percentage)
            # The first and last Months percentage needs to regard the day
            # Count of days in a month
            month_days = {
                1: 31,
                2: 28,
                3: 31,
                4: 30,
                5: 31,
                6: 30,
                7: 31,
                8: 31,
                9: 30,
                10: 31,
                11: 30,
                12: 31
            }
            if first:
                percentage = float(percentage) * (
                            (month_days[int(start_month)] + 1 - float(start_day)) / month_days[int(start_month)])
            if duration == 0:
                percentage = float(percentage) * (float(end_day) / month_days[int(start_month)])
            ass.responsibility = responsibility
            ass.save()

            # Prepare following iteration
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

    # RESTRICTION: USER SHALL NOT BE ABLE TO DELETE PAST ASSIGNMENTS
    end_date = datetime.strptime(str(end), format).date()
    today = datetime.today().date()
    if end_date < today:
        messages.error(request, "The Assignment already ended and will be kept to be reviewd.")
        return redirect('/data')

    # Calculate Assigments duration
    year_delta = int(end_year) - int(start_year)
    month_delta = int(end_month) - int(start_month)
    duration = 0
    if year_delta >= 0:
        duration += year_delta * 12 + month_delta
    # Delete all AssignmentPerMonth Objects belonging to Assignment
    while duration >= 0:
        start_month = int(start_month)
        month_name = month_dict[str(start_month)]
        month_obj = Month.objects.get(month=month_name, year=start_year)
        # Delete AssignmentPerMonth Object
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
    # Delete Assignment after all belonging AssignmentPerMonths Objects have been deleted
    assignment.delete()
    return redirect('/data')
