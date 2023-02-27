import re

from django import forms
from .models import Locations, Master, Student, Gyms


class FormLocationStepOne(forms.ModelForm):
    class Meta:
        model = Locations
        fields = ['province', 'name_city']

    def clean_name_city(self):
        name_city = self.cleaned_data.get('name_city')
        check_input = re.findall('[A-Za-z\s]+', name_city)
        if len(check_input) != 1:
            raise forms.ValidationError('name city must contain only letters .')
        elif len(check_input) == 1:
            if check_input[0] != name_city:
                raise forms.ValidationError('name city must contain only letters .')
        return name_city


class ChoiceTypeUser(forms.Form):
    TYPE_USER = [
        ('M', "Master"),
        ('S', "Student")
    ]
    type_user = forms.ChoiceField(choices=TYPE_USER)


class FormMasterStepTwo(forms.ModelForm):
    class Meta:
        model = Master
        fields = [
            'first_name',
            'last_name',
            'age',
            'gender',
            'profession',
            'number_phone',
            'national_code',
            'image_person'
        ]
        widgets = {
            'number_phone': forms.TextInput(attrs={'placeholder': 'start number with 09 for ex: 09358891234'}),
            'national_code': forms.TextInput(attrs={'placeholder': 'enter a national code contain numbers '}),
        }


class FormStudentStepThree(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "first_name",
            "last_name",
            "gender",
            "age",
            "image_person",
            "national_code",
            "number_phone",
        ]
        widgets = {
            'number_phone': forms.TextInput(attrs={'placeholder': 'start number with 09 for ex: 09358891234'}),
            'national_code': forms.TextInput(attrs={'placeholder': 'enter a national code contain numbers '})
        }


class FormGymsStepFour(forms.ModelForm):
    model = Gyms
    fields = [
        'name',
        'gender',
        'location',
        'field_sport_gym',
        'days_work',
        'time_start_working',
        'time_end_working',
        'capacity_gym',
        'state',
        'master',
        'monthly_tuition',
        'address_exact',
    ]


class ManagementForm(forms.Form):
    """
    ``ManagementForm`` is used to keep track of the current wizard step.
    """
    template_name = "django/forms/p.html"  # Remove when Django 5.0 is minimal version.
    current_step = forms.CharField(widget=forms.HiddenInput)