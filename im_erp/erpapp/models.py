from datetime import datetime
from django.db import models


# Create your models here.
class Month(models.Model):
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
    year_choices = [
        ('2020', '2020'),
        ('2021', '2021'),
        ('2022', '2022'),
        ('2023', '2023'),
        ('2024', '2024'),
        ('2025', '2025')
    ]
    month = models.CharField(max_length=10, choices=month_choices)
    year = models.CharField(max_length=5, choices=year_choices, default=str(datetime.now().strftime('%Y')))

    @property
    def name(self):
        return '{}, {}'.format(self.month, self.year)

    def short_name(self):
        return '{}{}'.format(self.month[:3], self.year[-2:])

    def __str__(self):
        return self.name


class Employee(models.Model):
    firstname = models.CharField('First Name', max_length=32)
    lastname = models.CharField('Last Name', max_length=32)
    type_choices = [
        ('Undergraduate Assistant', 'Undergraduate Assistant'),
        ('Research Assistant', 'Research Assistant')
    ]
    type = models.CharField('Type of Employment', choices=type_choices, max_length=32)
    capacity = models.FloatField('Capacity', default=1.0)
    hiring_date = models.DateField('Hiring Date')
    expiration_date = models.DateField('Expiration Date')

    @property
    def fullname(self):
        return '{} {}'.format(self.firstname, self.lastname)

    def __str__(self):
        return self.fullname

    class Meta:
        db_table = "employee"


class Task(models.Model):
    title = models.CharField('Title', max_length=50, default='Title')
    description = models.CharField('description', max_length=2400, default='Describe the task!')
    assigned_employees_on_month = models.ManyToManyField(Employee, through='AssignmentPerMonth')

    def __str__(self):
        return self.title

    class Meta:
        db_table = "task"


class Project(Task):
    ressources = models.FloatField('Ressources')
    begin = models.DateField('Project Start')
    duration = models.FloatField('Duration (in months)')
    end = models.DateField('Project End')

    def __str__(self):
        return self.title

    class Meta:
        db_table = "project"


class Position(Task):
    ressources = models.FloatField('Ressources')

    def __str__(self):
        return self.title

    class Meta:
        db_table = "position"


class Chair(Task):
    rotation_choices = [
        ('Summer Term', 'Summer Term'),
        ('Winter Term', 'Winter Term'),
        ('Every Term', 'Every Term'),
        ('Irregular', 'irregular')
    ]
    rotation = models.CharField('Term', default='Every Term', choices=rotation_choices, max_length=16)
    requirement = models.FloatField('Requirement', default=1)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "chair"


class AssignmentPerMonth(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    duration = models.IntegerField('Duration (in months)', default=0)
    percentage = models.FloatField('Functional Capacity', default=0.2)
    responsibility = models.BooleanField('Responsible', default=False)

    def __str__(self):
        return '{} --({})-> {} ({})'.format(self.employee, self.percentage, self.task, self.month)

    class Meta:
        db_table = "assignment_per_month"
