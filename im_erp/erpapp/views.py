from datetime import datetime

from django.shortcuts import render, redirect
from django.utils import timezone
from erpapp.forms import EmployeeForm, ProjectForm, PositionForm, ChairForm, AssignmentForm, EditAssignmentForm, \
    MonthForm
from django.contrib import messages
from erpapp.models import Employee, Project, Position, Chair, Assignment, Task, Month, AssignmentPerMonth


def index(request):
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
        'employees': employees,
        'projects': projects,
        'positions': positions,
        'chairs': chairs,
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


def employee_task_no_id(request):
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
    return redirect('/employee_task/{}'.format(month.id))


def employee_task(request, id):
    employees = Employee.objects.all()
    assignments_per_months = AssignmentPerMonth.objects.all()
    projects = Project.objects.all()
    chairs = Chair.objects.all()
    positions = Position.objects.all()
    tasks = Task.objects.all()
    employee_tasks = []
    employee_chairs_tasks = []
    employee_positions_tasks = []
    tasks_sum = []

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
        start_year, start_month = str(start).split('-')
        for month_obj in Month.objects.all():
            if month_obj.month == month_dict[str(int(start_month))] and month_obj.year == start_year:
                month_id = month_obj.id
                return redirect('/employee_task/{}'.format(month_id))
        return redirect('/employee_task/')

    month = Month.objects.get(id=id)

    # Loop through Project Tasks
    for employee in employees:
        employee_prj_hours = []
        employee_prj_hours_id = []
        for project in projects:
            for assignment_per_month in assignments_per_months:
                if assignment_per_month.task.id == project.id and assignment_per_month.employee.id == employee.id and assignment_per_month.month == month:
                    employee_prj_hours.append(
                        (int(round(assignment_per_month.percentage, 2) * 100), assignment_per_month.id, #hier!!!
                         assignment_per_month.responsibility))
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
            for assignment_per_months in assignments_per_months:
                if assignment_per_months.task.id == chair.id and assignment_per_months.employee.id == employee.id and assignment_per_months.month == month:
                    employee_ch_hours.append(
                        (int(round(assignment_per_months.percentage, 2) * 100), assignment_per_months.id,
                         assignment_per_months.responsibility))
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
            for assignment_per_months in assignments_per_months:
                if assignment_per_months.task.id == position.id and assignment_per_months.employee.id == employee.id and assignment_per_months.month == month:
                    employee_pos_hours.append(
                        (int(round(assignment_per_months.percentage, 2) * 100), assignment_per_months.id,
                         assignment_per_months.responsibility))
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
        for assignment_per_months in assignments_per_months:
            if assignment_per_months.task.id == project.id and assignment_per_months.month == month:
                sum += assignment_per_months.percentage

        tasks_sum.append(int(round(sum, 2) * 100))

    # Append (employee, workload)-Tuple employee_infos list
    employee_infos = []
    for employee in employees:
        employee_sum = 0
        for task in tasks:
            for assignment in Assignment.objects.all():
                if assignment.task.id == task.id and assignment.employee.id == employee.id:
                    employee_sum += assignment.percentage
        workload = employee_sum / employee.capacity
        employee_infos.append(
            (employee, int(round(employee_sum, 2) * 100), int(round(employee.capacity, 2) * 100), workload))

    date = timezone.now()
    current_year, current_month, _ = str(date).split('-')
    current_month_name = month_dict[str(int(current_month))]
    today = Month.objects.get(month=current_month_name, year=current_year)
    previous_month = Month.objects.get(id=id-1)
    next_month = Month.objects.get(id=id+1)
    context = {
        'employees': employees,
        'assignments': Assignment.objects.all(),
        'projects': projects,
        'chairs': chairs,
        'positions': positions,
        'employeetasks': employee_tasks,
        'tasks_sum': tasks_sum,
        'employee_infos': employee_infos,
        'month': month,
        'previous_month': previous_month,
        'next_month': next_month,
        'today': today,
    }
    return render(request, 'employee_task.html', context)

def employee_in_months(request):
    # data for one employee
    employee = Employee.objects.get(id = 1)
    position_in_months = []
    chair_in_months = []
    tasks_in_months = []

    # COLLECT DATA FOR PROJECTS FOR THIS EMPLOYEE
    for project in Project.objects.all():
        #collect all months
        allmonths = []
        for month in Month.objects.all():
            allmonths.append([month,0.0])
        # loop through all months and set their [1] to the percentage of the assignment
        i = 0
        for month in allmonths:
            for assignment_per_month in AssignmentPerMonth.objects.all():
                if project.id == assignment_per_month.task.id and assignment_per_month.employee.id == employee.id and month[0] == assignment_per_month.month:
                    allmonths[i][1] = assignment_per_month.percentage
            i = i + 1

        tasks_in_months.append(allmonths)

    # COLLECT DATA FOR POSTIONS FOR THIS EMPLOYEE
    for position in Position.objects.all():
        #collect all months
        allmonths = []
        for month in Month.objects.all():
            allmonths.append([month, 0.0])
        # loop through all months and set their [1] to the percentage of the assignment
        i = 0
        for month in allmonths:
            for assignment_per_month in AssignmentPerMonth.objects.all():
                if position.id == assignment_per_month.task.id and assignment_per_month.employee.id == employee.id and month[0] == assignment_per_month.month:
                    allmonths[i][1] = assignment_per_month.percentage
            i = i + 1

        tasks_in_months.append(allmonths)

    # COLLECT DATA FOR CHAIRS FOR THIS EMPLOYEE
    for chair in Chair.objects.all():
        # collect all months
        allmonths = []
        for month in Month.objects.all():
            allmonths.append([month,0.0])
        # loop through all months and set their [1] to the percentage of the assignment
        i = 0
        for month in allmonths:
            for assignment_per_month in AssignmentPerMonth.objects.all():
                if chair.id == assignment_per_month.task.id and assignment_per_month.employee.id == employee.id and month[0] == assignment_per_month.month:
                    allmonths[i][1] = assignment_per_month.percentage
            i = i + 1
    tasks_in_months.append(allmonths)
    print("list: ", tasks_in_months)

    return render(request, 'employee_in_months.html')


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
        start_year, start_month = str(start).split('-')
        for month_obj in Month.objects.all():
            if month_obj.month == month_dict[str(int(start_month))] and month_obj.year == start_year:
                month_id = month_obj.id
                return redirect('/employee_time/{}'.format(month_id))
        return redirect('/employee_time/')

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
        start_year, start_month = str(start).split('-')
        for month_obj in Month.objects.all():
            if month_obj.month == month_dict[str(int(start_month))] and month_obj.year == start_year:
                month_id = month_obj.id
                return redirect('/task_time/{}'.format(month_id))
        return redirect('/task_time/')

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


def add_new_emp(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():

            # Restrictions
            date_format = "%Y-%m-%d"
            if datetime.date(datetime.strptime(form.data['hiring_date'], date_format)) > \
                    datetime.date(datetime.strptime(form.data['expiration_date'], date_format)):
                messages.error(request, "The Employees contract expires before he got hired")
                return redirect('/add_new_ass')

            employee_firstname = form.data['firstname']
            employee_lastname = form.cleaned_data['lastname']
            for employee in Employee.objects.all():
                if employee.firstname == employee_firstname and employee.lastname == employee_lastname:
                    messages.error(request, "Employee already exists.")
                    return redirect('/add_new_emp')
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

            # Restrictions
            date_format = "%Y-%m-%d"
            if datetime.date(datetime.strptime(form.data['begin'], date_format)) > \
                    datetime.date(datetime.strptime(form.data['end'], date_format)):
                messages.error(request, "The Project ends before it started")
                return redirect('/add_new_ass')

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
    months = Month.objects.all()
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            # CHECK FOR DUPLICATES
            for assignment in Assignment.objects.all():
                if str(assignment.employee.id) == form.data['employee'] and \
                        str(assignment.task.id) == form.data['task']:
                    messages.error(request, "Emplyoee is already assigned to this task.")
                    return redirect('/add_new_ass')
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
                    messages.error(request, "This assignment would overbook postion( Title: " + Position.objects.get(
                        id=int(form.data['task'])).title + ").")
                    return redirect('/add_new_ass')
            # CHECK IF CHAIR ISNT OVERBOOKED
            # get ids of all chairs
            chairs = Chair.objects.all()
            chair_ids = []
            for chair in chairs:
                chair_ids.append(chair.id)
            # count assignments to current chair
            if int(form.data['task']) in chair_ids:
                count = 0
                for assignment in Assignment.objects.all():
                    if assignment.task.id == int(form.data['task']):
                        count = count + 1
                # check if count equal to requirement of current chair, if true dont allow assign
                if Chair.objects.get(id=int(form.data['task'])).requirement == count:
                    messages.error(request, "Chair " + Chair.objects.get(
                        id=int(form.data['task'])).title + " has already enough employees.")
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
            start_year, start_month, _ = str(form.data['start']).split('-')
            end_year, end_month, _ = str(form.data['end']).split('-')
            year_delta = int(end_year) - int(start_year)
            month_delta = int(end_month) - int(start_month)
            duration = 0
            if year_delta >= 0:
                duration += year_delta * 12 + month_delta
            # Use information to initialize AssignmentPerMonth Objects
            # as long as duration of Assignment is greater than zero
            while duration > 0:
                start_month = int(start_month)
                start_year = int(start_year)
                month_name = month_dict[str(start_month)]
                month_obj = Month.objects.get(month=month_name, year=start_year)
                # Create AssignmentPerMonth Object
                assignment_per_month = AssignmentPerMonth(employee=emp, task=task, month=month_obj, duration=duration,
                                                          percentage=form.data['percentage'],
                                                          responsibility=bool(form.data['responsibility']))
                assignment_per_month.save()

                # Increase the month and decrease the Assignments duration by one
                if start_month < 12:
                    start_month += 1
                else:
                    start_month = 1
                    start_year += 1
                duration -= 1

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
    assignment = Assignment.objects.get(id=id)
    # Get information about old timeframe before update
    start_year_old, start_month_old, _ = str(assignment.start).split('-')
    end_year_old, end_month_old, _ = str(assignment.end).split('-')
    print(assignment.start, assignment.end)
    form = EditAssignmentForm(request.POST, instance=assignment)
    if form.is_valid():
        # Get form data
        emp = Employee.objects.filter(id=assignment.employee.id).first()
        print('Emp:', emp)
        task = Task.objects.filter(id=assignment.task.id).first()
        print('Task:', task)
        percentage = form.data['percentage']
        try:
            responsibility = form.data['responsibility']
        except:
            responsibility = False

        # Restriction: User shall not be able to edit past assignments
        date_format = "%Y-%m-%d"
        start = form.data['start']
        start = datetime.strptime(start, date_format)
        today = datetime.today()
        if start < today:
            messages.error(request, "Cannot update Assignments in past months.")
            return redirect('/edit_ass/{}'.format(id))


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
        # Get information about the dates
        print(form.data)
        start_year, start_month, _ = str(form.data['start']).split('-')
        end_year, end_month, _ = str(form.data['end']).split('-')
        end_year_update, end_month_update, _ = str(form.data['end']).split('-')

        # Delete AssignmentPerMonths before and after the newly set timeframe:
        # start_old -> start    and    end -> end_old

        # Before: start_old -> start
        year_delta_before = int(start_year) - int(start_year_old)
        month_delta_before = int(start_month) - int(start_month_old)
        duration_before = 0
        if year_delta_before >= 0:
            duration_before += year_delta_before * 12 + month_delta_before
        # Use information to delete AssignmentPerMonth Objects (in timeframe start_old -> start)
        while duration_before > 0:
            print('Duration before:', duration_before)
            start_year_old = int(start_year_old)
            start_month_old = int(start_month_old)
            month_name = month_dict[str(start_month_old)]
            month_obj = Month.objects.get(month=month_name, year=start_year_old)
            print('Month before:', month_obj)
            # Delete AssignmentPerMonth Objects
            ass = AssignmentPerMonth.objects.get(employee=emp, task=task, month=month_obj)
            print('Assignment:', ass)
            ass.delete()
            # Iterator while loop
            if start_month_old < 12:
                start_month_old += 1
            else:
                start_month_old = 1
                start_year_old += 1
            duration_before -= 1

        # After: end -> end_old
        year_delta_after = int(end_year_old) - int(end_year)
        month_delta_after = int(end_month_old) - int(end_month)
        duration_after = 0
        if year_delta_after >= 0:
            duration_after += year_delta_after * 12 + month_delta_after
        # Use information to delete AssignmentPerMonth Objects (in timeframe end -> end_old)
        while duration_after > 0:
            print('Duration after:', duration_after)
            end_year = int(end_year)
            end_month = int(end_month)
            month_name = month_dict[str(end_month)]
            month_obj = Month.objects.get(month=month_name, year=end_year)
            print('Month after:', month_obj)
            # Delete AssignmentPerMonth Objects
            ass = AssignmentPerMonth.objects.get(employee=emp, task=task, month=month_obj)
            print('Assignment:', ass)
            ass.delete()
            # Iterator while loop
            if end_month < 12:
                end_month += 1
            else:
                end_month = 1
                end_year += 1
            duration_after -= 1

        # Update AssignmentPerMonths within the newly set timeframe
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
        while duration > 0:
            print('Duration:', duration)
            start_year = int(start_year)
            start_month = int(start_month)
            month_name = month_dict[str(start_month)]
            month_obj = Month.objects.get(month=month_name, year=start_year)
            print('Month:', month_obj)
            # Edit AssignmentPerMonth Object
            ass = AssignmentPerMonth.objects.get(employee=emp, task=task, month=month_obj)
            print('Assignment:', ass)
            ass.percentage = percentage
            ass.responsibility = responsibility
            ass.save()
            # Iterator while loop
            if start_month < 12:
                start_month += 1
            else:
                start_month = 1
                start_year += 1
            duration -= 1

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
    return redirect('/assignments')


def test(request, id):
    employees = Employee.objects.all()
    assignments_per_months = AssignmentPerMonth.objects.all()
    projects = Project.objects.all()
    chairs = Chair.objects.all()
    positions = Position.objects.all()
    tasks = Task.objects.all()
    employee_tasks = []
    employee_chairs_tasks = []
    employee_positions_tasks = []
    tasks_sum = []

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
        start_year, start_month = str(start).split('-')
        for month_obj in Month.objects.all():
            if month_obj.month == month_dict[str(int(start_month))] and month_obj.year == start_year:
                month_id = month_obj.id
                return redirect('/employee_task/{}'.format(month_id))
        return redirect('/employee_task/')

    month = Month.objects.get(id=id)

    # Loop through Project Tasks
    for employee in employees:
        employee_prj_hours = []
        employee_prj_hours_id = []
        for project in projects:
            for assignment_per_month in assignments_per_months:
                if assignment_per_month.task.id == project.id and assignment_per_month.employee.id == employee.id and assignment_per_month.month == month:
                    employee_prj_hours.append(
                        (int(round(assignment_per_month.percentage, 2) * 100), assignment_per_month.id,
                         assignment_per_month.responsibility))
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
            for assignment_per_months in assignments_per_months:
                if assignment_per_months.task.id == chair.id and assignment_per_months.employee.id == employee.id and assignment_per_months.month == month:
                    employee_ch_hours.append(
                        (int(round(assignment_per_months.percentage, 2) * 100), assignment_per_months.id,
                         assignment_per_months.responsibility))
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
            for assignment_per_months in assignments_per_months:
                if assignment_per_months.task.id == position.id and assignment_per_months.employee.id == employee.id and assignment_per_months.month == month:
                    employee_pos_hours.append(
                        (int(round(assignment_per_months.percentage, 2) * 100), assignment_per_months.id,
                         assignment_per_months.responsibility))
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
        for assignment_per_months in assignments_per_months:
            if assignment_per_months.task.id == project.id and assignment_per_months.month == month:
                sum += assignment_per_months.percentage
        ratio = sum / project.ressources
        tasks_sum.append((int(round(sum, 2) * 100), int(round(project.ressources, 2)) * 100, ratio))

    # Append (employee, workload)-Tuple to employee_infos list
    employee_infos = []
    for employee in employees:
        employee_sum = 0
        for task in tasks:
            for assignment in Assignment.objects.all():
                if assignment.task.id == task.id and assignment.employee.id == employee.id:
                    employee_sum += assignment.percentage
        workload = employee_sum / employee.capacity
        employee_infos.append(
            (employee, int(round(employee_sum, 2) * 100), int(round(employee.capacity, 2) * 100), workload))

    date = timezone.now()
    current_year, current_month, _ = str(date).split('-')
    current_month_name = month_dict[str(int(current_month))]
    today = Month.objects.get(month=current_month_name, year=current_year)
    previous_month = Month.objects.get(id=id - 1)
    next_month = Month.objects.get(id=id + 1)
    context = {
        'employees': employees,
        'assignments': Assignment.objects.all(),
        'projects': projects,
        'chairs': chairs,
        'positions': positions,
        'employeetasks': employee_tasks,
        'tasks_sum': tasks_sum,
        'employee_infos': employee_infos,
        'month': month,
        'previous_month': previous_month,
        'next_month': next_month,
        'today': today,
    }
    return render(request, 'employee_task_testpage.html', context)
