import re
from django import forms

from .models import MyUser


class FormRegisterUser(forms.ModelForm):
    re_password = forms.CharField(max_length=15, widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = [
            'username',
            'email',
            'password',
        ]
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean_re_password(self):
        password, re_password = self.cleaned_data.get('password'), self.cleaned_data.get('re_password')
        if password != re_password:
            raise forms.ValidationError('Password is not the same as repeat password ....')
        elif len(password) < 7:
            raise forms.ValidationError("Password must be longer than 7 characters ...")
        return password

    def clean_username(self):
        username = self.cleaned_data.get('username')
        check_username = re.findall('[a-zA-Z][a-zA-Z0-9]+', username)
        if MyUser.objects.filter(username=username).exists():
            raise forms.ValidationError("a user with this username registered ....")
        elif len(check_username) != 1:
            raise forms.ValidationError("username must contain words and numbers and must start with words ....")
        elif len(check_username) == 1:
            if check_username[0] != username:
                raise forms.ValidationError("username must contain words and numbers and must start with words ....")
        elif len(username) < 8:
            raise forms.ValidationError('Username must be longer than 8 characters ...')
        elif len(username) > 24:
            raise forms.ValidationError('Username must be less than 24 characters ...')

        return username


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class ChangePasswordForm(forms.Form):
    email = forms.EmailField()
    new_password = forms.CharField(widget=forms.PasswordInput)
    re_new_password = forms.CharField(widget=forms.PasswordInput)

