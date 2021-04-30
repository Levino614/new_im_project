from django.db import models


# Create your models here.
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
    title = models.CharField('Title', max_length=50, default='Task Title')
    description = models.CharField('description', max_length=2400)
    assigned_employees = models.ManyToManyField(Employee, through='Assignment')

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


class Assignment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    start = models.DateField('From')
    end = models.DateField('To')

    percentage = models.FloatField('Functional Capacity')
    responsibility = models.BooleanField('Responsible', default=False)

    def __str__(self):
        return '{} --({})-> {}'.format(self.employee, self.percentage, self.task)

    class Meta:
        db_table = "assignment"
