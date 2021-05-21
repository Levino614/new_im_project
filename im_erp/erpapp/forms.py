from django import forms
from erpapp.models import Employee, Project, Position, Chair, Assignment, Month


class EmployeeForm(forms.ModelForm):
    class Meta:
        # Takes all Employee Fields
        model = Employee
        fields = ['firstname', 'lastname', 'type', 'capacity', 'hiring_date', 'expiration_date']
        # Define the html input types
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
        # Takes all Project Fields
        model = Project
        fields = ['title', 'description', 'ressources', 'begin', 'end']
        # Define the html input types
        widgets = {'title': forms.TextInput(attrs={'class': 'form-control'}),
                   'description': forms.TextInput(attrs={'class': 'form-control'}),
                   'ressources': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0.0}),
                   'begin': forms.DateInput(attrs={'class': 'form-control'}),
                   'end': forms.DateInput(attrs={'class': 'form-control'}),
                   }


class PositionForm(forms.ModelForm):
    class Meta:
        # Takes all Chair Position Fields
        model = Position
        fields = ['title', 'description', 'ressources']
        # Define the html input types
        widgets = {'title': forms.TextInput(attrs={'class': 'form-control'}),
                   'description': forms.TextInput(attrs={'class': 'form-control'}),
                   'ressources': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0.0}),
                   }


class ChairForm(forms.ModelForm):
    class Meta:
        # Takes all Chair Task Fields
        model = Chair
        fields = ['title', 'description', 'rotation', 'requirement']
        # Define the html input types
        widgets = {'title': forms.TextInput(attrs={'class': 'form-control'}),
                   'description': forms.TextInput(attrs={'class': 'form-control'}),
                   'rotation': forms.Select(attrs={'class': 'form-control'}),
                   'requirement': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0.0}),
                   }


class AssignmentForm(forms.ModelForm):
    class Meta:
        # Takes all Assignment Fields
        model = Assignment
        fields = ['employee', 'task', 'start', 'end', 'percentage', 'responsibility', 'comment']
        # Define the html input types
        widgets = {'employee': forms.Select(attrs={'class': 'form-control'}),
                   'task': forms.Select(attrs={'class': 'form-control'}),
                   'start': forms.DateInput(attrs={'class': 'form-control'}),
                   'end': forms.DateInput(attrs={'class': 'form-control'}),
                   'percentage': forms.NumberInput(
                       attrs={'class': 'form-control', 'step': '0.01', 'max': 1.0, 'min': 0.0}),
                   'responsibility': forms.NullBooleanSelect(attrs={'class': 'form-control'}),
                   'comment': forms.TextInput(attrs={'class': 'form-control'}),
                   }


# For editing an assignment
class EditAssignmentForm(forms.ModelForm):
    class Meta:
        # Takes all Assignment Fields except the employee and task
        model = Assignment
        exclude = ['employee', 'task']

