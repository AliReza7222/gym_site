import environs
import random
from string import digits

from accounts.models import MyUser
from gyms.models import Student, Master
from accounts.views import show_first_error
from .forms import FormPaymentSimulator
from .mixin import CheckUserStudentMixin, CheckUserMasterMixin

from django.views.generic import FormView
from django.urls import reverse
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import JsonResponse
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
                messages.error(request, 'Your unique code has expired.')

            elif data_confirm.get('phone_number') != user.student.number_phone:
                cache.delete(user.student.id)
                messages.error(request, 'The Phone Number you entered is not the same as the registration Phone Number.')
                messages.error(request, 'Your unique code has expired.')

            elif cache.get(user.student.id) is not None and cache.get(user.student.id) != data_confirm.get('code_send'):
                cache.delete(user.student.id)
                messages.error(request, 'The entered code is incorrect.')
                messages.error(request, 'Your unique code has expired.')

            elif cache.get(user.student.id) is None:
                messages.error(request, 'Your unique code has expired.')

            else:
                user.student.credit += data_confirm.get('credit_student')
                user.student.save()
                messages.success(request, f"Your account {data_confirm.get('credit_student')} money was charged .")
                return redirect('home')
            return redirect('payment_simulator')

        message = show_first_error(for_obj.errors)
        messages.error(request, f'{message.get("field")}: {message.get("text").lstrip("*")}\n and Your unique code has expired.')
        return redirect(reverse('payment_simulator'))


class CreateCodePaymentSimulator(LoginRequiredMixin, FormView):
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
        if request.user.type_user == 'S':
            key_user = str(request.user.student.id)
            cache.set(key_user, code, timeout=78)
        elif request.user.type_user == 'M':
            key_user = str(request.user.master.id)
            cache.set(key_user, code, timeout=78)
        # note send email
        message_success_send = 'The payment code has been sent to your email !'
        return JsonResponse({'message': message_success_send})


class MoneyTransferSimulator(LoginRequiredMixin, CheckUserMasterMixin, FormView):
    login_url = 'login'
    template_name = 'payment/money_transfer_simulator.html'
    form_class = FormPaymentSimulator

    def post(self, request, *args, **kwargs):
        data = request.POST
        form_obj = FormPaymentSimulator(data)
        if form_obj.is_valid():
            data_confirm = form_obj.cleaned_data
            student_user = Student.objects.filter(number_phone=data_confirm.get('phone_number'),
                                                  user__email=data_confirm.get('email'))
            master_user = Master.objects.filter(number_phone=data_confirm.get('phone_number'),
                                                user__email=data_confirm.get('email'))
            amount_money = data_confirm.get('credit_student')
            if not (student_user or master_user):
                cache.delete(request.user.master.id)
                messages.error(request, 'There is no user with this email and phone number.')
                messages.error(request, 'Your unique code has expired.')
            elif form_obj.errors:
                cache.delete(request.user.master.id)
                message = show_first_error(form_obj.errors)
                messages.error(request, f'{message.get("field")}: {message.get("text").lstrip("*")}')
                messages.error(request, 'Your unique code has expired.')
            elif cache.get(request.user.master.id) != data_confirm.get('code_send') and cache.get(request.user.master.id) is not None:
                cache.delete(request.user.master.id)
                messages.error(request, 'The entered code is incorrect.')
                messages.error(request, 'Your unique code has expired.')

            elif cache.get(request.user.master.id) is None:
                messages.error(request, 'Your unique code has expired.')

            elif amount_money > request.user.master.salary:
                cache.delete(request.user.master.id)
                messages.error(request, "You don't have that much money.")
                messages.error(request, 'Your unique code has expired.')
            elif master_user:
                if master_user[0].id == request.user.master.id:
                    cache.delete(request.user.master.id)
                    messages.error(request, 'This Information is for yours !!!!!!')
                    messages.error(request, 'Your unique code has expired.')
            else:
                master = request.user.master

                if student_user:
                    student_id = student_user[0].id
                    student = Student.objects.get(id=student_id)
                    student.credit += amount_money
                    student.save()
                elif master_user:
                    master_id = master_user[0].id
                    master_other = Master.objects.get(id=master_id)
                    master_other.salary += amount_money
                    master_other.save()

                master.salary -= amount_money
                master.save()

                message = f'The money {amount_money} $ transfer was successful to email user \"{data_confirm["email"]}\"'
                messages.success(request, message)
                return redirect('home')

        return redirect('money_transfer')
