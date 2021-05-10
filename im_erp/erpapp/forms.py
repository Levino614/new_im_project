from django import forms
from erpapp.models import Employee, Project, Position, Chair, Assignment, Month


class EmployeeForm(forms.ModelForm):
    class Meta:
        type_choices = [
            ('UA', 'Undergraduate Assistant'),
            ('RA', 'Research Assistant')
        ]
        model = Employee
        fields = ['firstname', 'lastname', 'type', 'capacity', 'hiring_date', 'expiration_date']
        widgets = {'firstname': forms.TextInput(attrs={'class': 'form-control'}),
                   'lastname': forms.TextInput(attrs={'class': 'form-control'}),
                   'type': forms.Select(attrs={'class': 'form-control'}),
                   'capacity': forms.NumberInput(attrs={'class': 'form-control',
                                                        'step': '0.01', 'max': 1.0, 'min': 0.0}),
                   'hiring_date': forms.DateInput(attrs={'class': 'form-control'}),
                   'expiration_date': forms.DateInput(attrs={'class': 'form-control'}),
                   }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'ressources', 'begin', 'end']
        widgets = {'title': forms.TextInput(attrs={'class': 'form-control'}),
                   'description': forms.TextInput(attrs={'class': 'form-control'}),
                   'ressources': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0.0}),
                   'begin': forms.DateInput(attrs={'class': 'form-control'}),
                   'end': forms.DateInput(attrs={'class': 'form-control'}),
                   }


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['title', 'description', 'ressources']
        widgets = {'title': forms.TextInput(attrs={'class': 'form-control'}),
                   'description': forms.TextInput(attrs={'class': 'form-control'}),
                   'ressources': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0.0}),
                   }


class ChairForm(forms.ModelForm):
    class Meta:
        rotation_choices = [
            ('Summer Term', 'Summer Term'),
            ('Winter Term', 'Winter Term'),
            ('Every Term', 'Every Term'),
            ('Irregular', 'Irregular')
        ]
        model = Chair
        fields = ['title', 'description', 'rotation', 'requirement']
        widgets = {'title': forms.TextInput(attrs={'class': 'form-control'}),
                   'description': forms.TextInput(attrs={'class': 'form-control'}),
                   'rotation': forms.Select(attrs={'class': 'form-control'}),
                   'requirement': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0.0}),
                   }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['employee', 'task', 'start', 'end', 'percentage', 'responsibility', 'comment']
        widgets = {'employee': forms.Select(attrs={'class': 'form-control'}),
                   'task': forms.Select(attrs={'class': 'form-control'}),
                   'start': forms.DateInput(attrs={'class': 'form-control'}),
                   'end': forms.DateInput(attrs={'class': 'form-control'}),
                   'percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'max': 1.0, 'min': 0.0}),
                   'responsibility': forms.NullBooleanSelect(attrs={'class': 'form-control'}),
                   'comment': forms.TextInput(attrs={'class': 'form-control'}),
                   }


class EditAssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        exclude = ['employee', 'task']


class MonthForm(forms.ModelForm):
    class Meta:
        type_choices = [
            ('UA', 'Undergraduate Assistant'),
            ('RA', 'Research Assistant')
        ]
        model = Month
        fields = ['month', 'year']
        widgets = {'month': forms.Select(attrs={'class': 'form-control'}),
                   'year': forms.Select(attrs={'class': 'form-control'}),
                   }
