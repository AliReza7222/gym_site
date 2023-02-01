from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.views.generic import CreateView

from .models import MyUser
from .forms import FormRegisterUser


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
            messages.success(request, 'Create account successfully !')
            return redirect('register')
        messages.error(request, 'Account could not be created, pay attention to the errors')
        return render(request, self.template_name, context={'form': form})


