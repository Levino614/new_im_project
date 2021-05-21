import datetime
from django.db import models
from django.utils import timezone


class Month(models.Model):
    # Months choice from Jan to Dec
    month_choices = [
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December')
    ]
    month = models.CharField(max_length=10, choices=month_choices)
    # Year choice from -10 to +10 years from now
    year_choices = [(str(r), str(r)) for r in range(datetime.date.today().year - 10, datetime.date.today().year + 10)]
    year = models.CharField(max_length=5, choices=year_choices, default=str(timezone.now().strftime('%Y')))

    # Returns month and year as a string
    @property
    def name(self):
        return '{}, {}'.format(self.month, self.year)

    # Returns month and year as a shorter string
    def short_name(self):
        return '{}{}'.format(self.month[:3], self.year[-2:])

    # Standard string representation when printing month objects
    def __str__(self):
        return self.name

    class Meta:
        db_table = "month"
        unique_together = ('month', 'year')


class Employee(models.Model):
    firstname = models.CharField('First Name', max_length=32)  # Employees first name
    lastname = models.CharField('Last Name', max_length=32)  # Employees last name
    # Employment type choices
    type_choices = [
        ('Undergraduate Assistant', 'Undergraduate Assistant'),
        ('Research Associate', 'Research Associate')
    ]
    type = models.CharField('Type of Employment', choices=type_choices, max_length=32)
    capacity = models.FloatField('Capacity', default=1.0)  # Total capacity of an employee
    hiring_date = models.DateField('Hiring Date')  # Start of contract
    expiration_date = models.DateField('Expiration Date')  # End of contract

    # Returns first and last name as a string
    @property
    def fullname(self):
        return '{} {}'.format(self.firstname, self.lastname)

    # Returns hiring date as a string
    @property
    def hiring_date_formatted(self):
        return str(self.hiring_date)

    # Returns expiration date as a string
    @property
    def expiration_date_formatted(self):
        return str(self.expiration_date)

    # Standard string representation when printing employee objects
    def __str__(self):
        return self.fullname

    class Meta:
        db_table = "employee"
        unique_together = ('firstname', 'lastname')


# Superclass for all different tasks (Projects, (Chair) Positions , Chair (Tasks))
class Task(models.Model):
    title = models.CharField('Title', max_length=50, default='Title', unique=True)  # Title of the task
    description = models.CharField('Description', max_length=2400, default='Describe the task!')  # Describes the task
    # assigned_employees_on_month = models.ManyToManyField(Employee, through='AssignmentPerMonth')  # Not used

    # Standard string representation when printing Task objects
    def __str__(self):
        return self.title

    class Meta:
        db_table = "task"


# Project inherits from Task Object
class Project(Task):
    # Additional fields:
    ressources = models.FloatField('Ressources')  # Projects max available ressources (can be overbooked)
    begin = models.DateField('Project Start')  # Begin of the project
    end = models.DateField('Project End')  # Scheduled End of the project

    # Returns begin date as a string
    @property
    def begin_formatted(self):
        return str(self.begin)

    # Returns end date as a string
    @property
    def end_formatted(self):
        return str(self.end)

    class Meta:
        db_table = "project"


# Chair Position inherits from Task Object
class Position(Task):
    # Chair Positions max available ressources (cannot be overbooked -> restricted in view: add_pos)
    ressources = models.FloatField('Ressources')

    class Meta:
        db_table = "position"


# Chair Task inherits from Task Object
class Chair(Task):
    # Choice of rotation
    rotation_choices = [
        ('Summer Term', 'Summer Term'),
        ('Winter Term', 'Winter Term'),
        ('Every Term', 'Every Term'),
        ('Irregular', 'irregular')
    ]
    rotation = models.CharField('Term', default='Every Term', choices=rotation_choices, max_length=16)
    requirement = models.FloatField('Requirement', default=1)  # Requirement of Employee

    class Meta:
        db_table = "chair"


# Automatically created when new assignment objects are added (view: add_ass)
class AssignmentPerMonth(models.Model):
    # Employees assignment to a task in a specific month
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    duration = models.IntegerField('Duration (in months)', default=0)  # Not used yet
    # The percentage by that the employee works on the task in that month
    # Regards the day in first and last month to adjust percentage accordingly
    percentage = models.FloatField('Functional Capacity', default=0.2)
    responsibility = models.BooleanField('Responsible', default=False)  # Is employee responsible for task?

    # Standard string representation when printing AssignmentPerMonth objects
    def __str__(self):
        return '{} --({})-> {} ({})'.format(self.employee, self.percentage, self.task, self.month)

    class Meta:
        db_table = "assignment_per_month"
        unique_together = ('employee', 'task', 'month')


class Assignment(models.Model):
    # Assignment of employee to task
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    start = models.DateField('From', default=timezone.now().date())  # Start of the Assignment
    end = models.DateField('To', default=timezone.now().date())  # End of the project
    percentage = models.FloatField('Functional Capacity', default=0.2)  # Percentage by that an employee works on a task
    responsibility = models.BooleanField('Responsible', default=False)  # Is employee responsible for task?
    comment = models.CharField('Comment', max_length=2400, default='-')  # Comment on the assignment

    # Returns start date as a string
    @property
    def start_formatted(self):
        return str(self.start)

    # Returns end date as a string
    @property
    def end_formatted(self):
        return str(self.end)

    # Standard string representation when printing Assignment objects
    def __str__(self):
        return '{} --({})-> {}'.format(self.employee, self.percentage, self.task)

    class Meta:
        db_table = "assignment"
