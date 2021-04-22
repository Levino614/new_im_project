from django import forms
from erpapp.models import Employee


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
                   'capacity': forms.NumberInput(attrs={'class': 'form-control', 'step': "0.1"}),
                   'hiring_date': forms.DateInput(attrs={'class': 'form-control'}),
                   'expiration_date': forms.DateInput(attrs={'class': 'form-control'}),
                   }

