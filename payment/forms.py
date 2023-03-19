import re
from django import forms


class FormPaymentSimulator(forms.Form):
    credit_student = forms.IntegerField(min_value=0)
    phone_number = forms.CharField(max_length=11)
    email = forms.EmailField()
    code_send = forms.CharField(max_length=30)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        get_regex_phone_number = re.findall('^09[0-9]{9}$', phone_number)
        if get_regex_phone_number:
            if get_regex_phone_number[0] == phone_number:
                return phone_number
        raise forms.ValidationError('number phone must be contain 11 number and start with 09 .')

    def clean_code_send(self):
        code_send_get = self.cleaned_data.get('code_send')
        if not code_send_get.isdigit():
            return forms.ValidationError('Wrong Code !')
        return code_send_get
