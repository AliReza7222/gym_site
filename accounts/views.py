from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.views.generic import CreateView, FormView
from django.urls import reverse_lazy
from django.contrib.auth import login, logout, authenticate

from .models import MyUser
from .forms import FormRegisterUser, LoginForm, ChangePasswordForm


class RegisterUser(CreateView):
    model = MyUser
    template_name = 'accounts/register.html'
    context_object_name = 'user_objects'
    form_class = FormRegisterUser

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.cleaned_data.pop('re_password')
            data = form.cleaned_data
            user_obj = MyUser.objects.create(**data)
            user_obj.password = make_password(data.get('password'))
            user_obj.save()
            messages.success(request, 'Create account successfully , now you can login !')
            return redirect('home')
        messages.error(request, 'Account could not be created, pay attention to the errors')
        return render(request, self.template_name, context={'form': form})


class LoginUser(FormView):
    template_name = 'accounts/login.html'
    form_class = LoginForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            email, password = data.get('email'), data.get('password')
            check_email = MyUser.objects.filter(email=email).exists()
            if not check_email:
                messages.error(request, 'The password or email is incorrect ....')
                return redirect('login')
            elif check_email:
                user = MyUser.objects.get(email=email)
                password_user = user.password
                if check_password(password, password_user):
                    login(request, user)
                    messages.success(request, 'login successfully !')
                    return redirect('home')
                messages.error(request, 'The password or email is incorrect ....')
                return redirect('login')
        messages.error(request, 'The password or email is incorrect ....')
        return redirect('login')


class ChangePassword(FormView):
    form_class = ChangePasswordForm
    template_name = 'accounts/change_password.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            email = data.get('email')
            new_password, re_new_password = data.get('new_password'), data.get('re_new_password')
            if MyUser.objects.filter(email=email).exists():
                user = MyUser.objects.get(email=email)
                if new_password == re_new_password:
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'changed password your account')
                    return redirect('login')
                messages.error(request, 'Password is not the same as repeat password')
                return redirect('change_password')
            messages.error(request, 'email is incorrect ')
            return redirect('change_password')
