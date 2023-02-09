import re

from django import forms
from .models import Locations, Master, Student, Gyms


class FormLocationStepOne(forms.ModelForm):
    class Meta:
        model = Locations
        fields = ['province', 'name_city']

    def clean_name_city(self):
        name_city = self.cleaned_data.get('name_city')
        check_input = re.findall('[A-Za-z]+', name_city)
        if len(check_input) != 1:
            raise forms.ValidationError('This field must contain only letters .')
        elif len(check_input) == 1:
            if check_input[0] != name_city:
                raise forms.ValidationError('This field must contain only letters .')
        return name_city


class FormMasterStepTwo(forms.ModelForm):
    class Meta:
        model = Master
        fields = [

        ]
