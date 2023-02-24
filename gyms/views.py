import os.path
import sys

from accounts.views import show_first_error
from .models import Locations, Master, Student, MyUser
from .mixins import CheckCompleteProfileMixin, CheckNotCompleteProfileMixin
from .forms import (FormLocationStepOne, FormMasterStepTwo,
                    ChoiceTypeUser, FormStudentStepThree, FormGymsStepFour, ManagementForm)

from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.conf import settings
from formtools.wizard.views import SessionWizardView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.views.generic import TemplateView, DetailView


class Home(TemplateView):
    template_name = 'gyms/home.html'


class About(TemplateView):
    template_name = 'gyms/about.html'


class ProfileUser(LoginRequiredMixin, CheckCompleteProfileMixin, SessionWizardView):
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'image'))
    login_url = 'login'
    template_name = 'gyms/profile.html'
    STEP_ONE, STEP_TWO, STEP_THREE, STEP_FOUR = '0', '1', '2', '3'

    def check_type_user_master(self):
        data = self.storage.get_step_data('1')
        if data is not None:
            step_form = data.get('profile_user-current_step')
            if step_form == '1':
                if data.get('1-type_user') == 'M':
                    return True
                return False

    def check_type_user_student(self):
        data = self.storage.get_step_data('1')
        if data is not None:
            step_form = data.get('profile_user-current_step')
            if step_form == '1':
                if data.get('1-type_user') == 'S':
                    return True
                return False

    def return_true(self):
        return True

    condition_dict = {
        STEP_ONE: return_true,
        STEP_TWO: return_true,
        STEP_THREE: check_type_user_master,
        STEP_FOUR: check_type_user_student
    }

    form_list = [
        (STEP_ONE, FormLocationStepOne),
        (STEP_TWO, ChoiceTypeUser),
        (STEP_THREE, FormMasterStepTwo),
        (STEP_FOUR, FormStudentStepThree)
    ]

    def post(self, *args, **kwargs):

        # location data checked and if no exists save in database
        if self.steps.current == self.STEP_ONE:
            data = self.request.POST
            form_obj = self.get_form(step=self.STEP_ONE, data=data)
            if form_obj.is_valid():
                clean_data = {'province': data.get('0-province'), 'name_city': data.get('0-name_city').title()}
                # create or get object location with data in request POST
                obj, created = Locations.objects.get_or_create(**clean_data)

        # Look for a wizard_goto_step element in the posted data which
        # contains a valid step name. If one was found, render the requested
        # form. (This makes stepping back a lot easier).
        wizard_goto_step = self.request.POST.get('wizard_goto_step', None)
        if wizard_goto_step and wizard_goto_step in self.get_form_list():
            return self.render_goto_step(wizard_goto_step)
        # Check if form was refreshed
        management_form = ManagementForm(self.request.POST, prefix=self.prefix)
        if not management_form.is_valid():
            raise ValidationError(
                'ManagementForm data is missing or has been tampered.',
                code='missing_management_form',
            )
        form_current_step = management_form.cleaned_data['current_step']
        if (form_current_step != self.steps.current and
                self.storage.current_step is not None):
            # form refreshed, change current step
            self.storage.current_step = form_current_step
        # get the form for the current step
        form = self.get_form(data=self.request.POST, files=self.request.FILES)
        # and try to validate
        if form.is_valid():
            # if the form is valid, store the cleaned data and files.
            self.storage.set_step_data(self.steps.current, self.process_step(form))
            self.storage.set_step_files(self.steps.current, self.process_step_files(form))
            # check if the current step is the last step
            if self.steps.current == self.steps.last:
                # no more steps, render done view
                return self.render_done(form, **kwargs)
            else:
                # proceed to the next step
                return self.render_next_step(form)
        # show error field
        message_box = show_first_error(form.errors)
        messages.error(self.request, f"{message_box.get('field')}:  {message_box.get('text').lstrip('*')}")
        return self.render(form)

    def done(self, form_list, **kwargs):
        steps = self.steps.all
        # assignment type user to model user
        type_user = self.get_cleaned_data_for_step('1').get('type_user')
        user = self.request.user
        user.type_user = type_user
        user.save()

        # get object location
        data_location = self.get_cleaned_data_for_step('0')
        obj_location = Locations.objects.filter(province=data_location.get('province'),
                                                name_city=data_location.get('name_city').title()).first()

        # Handel step information user Master
        if self.STEP_THREE in steps:
            data_info = self.get_cleaned_data_for_step(self.STEP_THREE)
            data_info['location'] = obj_location
            data_info['user'] = user
            Master.objects.create(**data_info)

        # Handel step information user Student
        elif self.STEP_FOUR in steps:
            data_info = self.get_cleaned_data_for_step(self.STEP_FOUR)
            data_info['location'] = obj_location
            data_info['user'] = user
            Student.objects.create(**data_info)

        messages.success(self.request, 'Create Your Profile .')
        return redirect('home')


class ShowProfile(LoginRequiredMixin, CheckNotCompleteProfileMixin, DetailView):
    model = MyUser
    login_url = 'login'
    template_name = 'gyms/detail_profile.html'

    def get_context_data(self, **kwargs):
        """Insert the single object into the context dict."""
        context = {}
        user = self.request.user
        # check in user have master or have student
        master, student = Master.objects.filter(user=user), Student.objects.filter(user=user)
        if self.object:
            context["object"] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        if master:
            context['info_prof'] = master[0]
            context['type_user'] = 'Master'
        elif student:
            context['info_prof'] = student[0]
            context['type_user'] = 'Student'
        context.update(kwargs)
        return super().get_context_data(**context)
