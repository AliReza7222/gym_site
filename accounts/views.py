import random
import environs
import re

from string import digits, ascii_letters

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.views.generic import CreateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.contrib.auth import login, logout, authenticate

from .models import MyUser
from gyms.models import Student
from .forms import FormRegisterUser, LoginForm, ChangePasswordForm, ChangePasswordWithUserForm
from conversation.views import return_type_info_note


# a variable env create
env = environs.Env()
env.read_env()


def show_first_error(list_error):
    for field in list_error:
        if list_error.get(field):
            return {'field': field, 'text': list_error.get(field).as_text()}


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
        message = show_first_error(form.errors)
        messages.error(request, f'{message.get("field")} : {message.get("text").lstrip("*")}')
        return render(request, self.template_name, context={'form': form})


class LoginUser(FormView):
    template_name = 'accounts/login.html'
    form_class = LoginForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username, password = data.get('username'), data.get('password')
            check_email = MyUser.objects.filter(username=username).exists()
            if not check_email:
                messages.error(request, 'The password or username is incorrect ....')
                return redirect('login')
            elif check_email:
                user = MyUser.objects.get(username=username)
                password_user = user.password
                if check_password(password, password_user):
                    login(request, user)
                    if user.type_user == 'S':
                        student = Student.objects.get(user=user)
                        type_new_notification = return_type_info_note(student)
                        if student.new_notification != '0' and type_new_notification == str:
                            messages.info(request, "You have New Notification please check your gym's inbox")
                            student.new_notification = str(re.findall('gym \w+ ',
                                                                      student.new_notification)[0].strip().split(' '))
                            student.save()
                    messages.success(request, 'login successfully !')
                    if request.GET.get('next'):
                        return redirect(request.GET.get('next'))
                    return redirect('home')
                messages.error(request, 'The password or username is incorrect ....')
                return redirect('login')
        messages.error(request, 'The password or username is incorrect ....')
        return redirect('login')


class ChangePassword(FormView):
    form_class = ChangePasswordForm
    template_name = 'accounts/change_password.html'

    def generate_password(self):
        list_words = list(digits + ascii_letters)
        new_password = ''
        for word in range(7):
            new_password += random.choice(list_words)
        return new_password

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            username, email = data.get('username'), data.get('email')
            get_user = MyUser.objects.filter(email=email, username=username)
            if not get_user.exists():
                messages.error(request, 'incorrect information .')
                return redirect('change_password')
            elif get_user.exists():
                user = get_user[0]
                new_password = self.generate_password()
                # send Email
                subject_mail = 'New Password your account Gym'
                message = f'Hello mrs/mis {user} your new password account is "{new_password}" .'
                from_email = env('FROM_EMAIL')
                recipient_list = [email]
                send_mail(subject_mail, message, from_email, recipient_list)
                # set new password
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Your new password send to your email .')
                return redirect('login')
        messages.error(request, show_first_error(form.errors).get('text'))
        return redirect('change_password')


class LogoutUser(LoginRequiredMixin, FormView):
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        confirm_logout = request.GET.get('result') or False
        if confirm_logout == 'true':
            logout(request)
            messages.success(request, 'Logout Successfully !')
            return redirect('home')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class ChangePasswordWithUser(LoginRequiredMixin, FormView):
    login_url = 'login'
    template_name = 'accounts/change_password_user.html'
    form_class = ChangePasswordWithUserForm

    def post(self, request, *args, **kwargs):
        data = request.POST
        user = request.user
        obj_form = self.form_class(data)

        if obj_form.is_valid():
            data_confirmed = obj_form.cleaned_data
            checked_past_password = check_password(data_confirmed.get('past_password'), user.password)
            if not checked_past_password:
                messages.error(request, 'Past Password Incorrect !')
                return redirect('change_password_with_user')
            elif checked_past_password:
                new_password = data_confirmed.get('new_password')
                user.set_password(new_password)
                user.save()
                login(request, user)
                messages.success(request, 'successfully changing password .')
                return redirect('profile')
        message_error = show_first_error(obj_form.errors)
        messages.error(request, message_error.get('text').lstrip('*'))
        return redirect('change_password_with_user')