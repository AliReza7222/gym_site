import environs
import random
import time
import json
from string import digits

from accounts.models import MyUser
from gyms.models import Student
from accounts.views import show_first_error
from .forms import FormPaymentSimulator
from .mixin import CheckUserStudentMixin

from django.views.generic import FormView
from django.urls import reverse
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import QueryDict, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin


# a variable env create
env = environs.Env()
env.read_env()


class PaymentGatewaySimulator(LoginRequiredMixin, CheckUserStudentMixin, FormView):
    login_url = 'login'
    template_name = 'payment/payment_simulator.html'
    form_class = FormPaymentSimulator

    def post(self, request, *args, **kwargs):
        data = request.POST
        user = request.user
        for_obj = FormPaymentSimulator(data)
        if for_obj.is_valid():
            data_confirm = for_obj.cleaned_data
            if data_confirm.get('email') != user.email:
                cache.delete(user.student.id)
                messages.error(request, 'The email you entered is not the same as the registration email.')

            elif data_confirm.get('phone_number') != user.student.number_phone:
                cache.delete(user.student.id)
                messages.error(request, 'The Phone Number you entered is not the same as the registration Phone Number.')

            elif cache.get(user.student.id) is not None and cache.get(user.student.id) != data_confirm.get('code_send'):
                cache.delete(user.student.id)
                messages.error(request, 'The entered code is incorrect.')

            elif cache.get(user.student.id) is None:
                messages.error(request, 'Your unique code has expired.')

            else:
                user.student.credit += data_confirm.get('credit_student')
                user.student.save()
                messages.success(request, f"Your account {data_confirm.get('credit_student')} money was charged .")
                return redirect('home')
            return redirect('payment_simulator')

        message = show_first_error(for_obj.errors)
        messages.error(request, f'{message.get("field")}: {message.get("text").lstrip("*")}')
        return redirect(reverse('payment_simulator'))


class FieldStudentPaymentSimulator(LoginRequiredMixin, CheckUserStudentMixin, FormView):
    login_url = 'login'
    form_class = FormPaymentSimulator

    def generate_code(self):
        my_list = list(digits)
        my_code = ''
        for digit in range(6):
            my_code += random.choice(my_list)
        return my_code

    def get(self, request, *args, **kwargs):
        # code unique generate
        code = self.generate_code()
        # send email
        subject_mail = 'Gym payment code'
        message = f"Your Code Payment is {code} ."
        from_email = env('FROM_EMAIL')
        recipient_list = [request.user.email]
        send_mail(subject_mail, message, from_email, recipient_list)
        # set in code cache
        key_user = str(request.user.student.id)
        cache.set(key_user, code, timeout=78)
        # note send email
        message_success_send = 'The payment code has been sent to your email !'
        return JsonResponse({'message': message_success_send})
