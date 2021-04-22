from datetime import timedelta
from django.db import models


# Create your models here.
class Employee(models.Model):
    firstname = models.CharField('First Name', max_length=32)
    lastname = models.CharField('Last Name', max_length=32)
    type_choices = [
        ('UA', 'Undergraduate Assistant'),
        ('RA', 'Research Assistant')
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
    name = models.CharField('Titel', max_length=50)
    description = models.CharField('Beschreibung', max_length=2400)

    def __str__(self):
        return self.name


class Project(Task):
    ressources = models.FloatField('Ressources')
    begin = models.DateField('Project Start')
    duration = models.DurationField('Duration')
    end = models.DateField('Project End')

    def __str__(self):
        return self.name


class Position(Task):
    ressources = models.FloatField('Ressources')

    def __str__(self):
        return self.name


class Chair(Task):
    rotation_choices = [
        ('ST', 'Sommer Term'),
        ('WT', 'Winter Term'),
        ('ET', 'Every Term'),
        ('irreg', 'irregular')
    ]
    rotation = models.CharField('Term', default='Every Term', choices=rotation_choices, max_length=16)
    requirement = models.FloatField('Requirement', default=1)

    def __str__(self):
        return self.name


class Assignment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    start = models.DateField('From')
    end = models.DateField('To')
    percentage = models.FloatField('Functional Capacity')
    responsibility = models.BooleanField('Responsible', default=False)

    def __str__(self):
        return '{} --({})-> {}'.format(self.employee, self.percentage, self.task)
