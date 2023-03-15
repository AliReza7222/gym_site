import os.path

from accounts.views import show_first_error
from .validations import get_words
from accounts.forms import FormRegisterUser
from .models import Locations, Master, Student, MyUser, Gyms, FIELD_SPORTS_CHOICE
from .mixins import CheckCompleteProfileMixin, CheckNotCompleteProfileMixin, CheckUserMasterMixin, CheckGymMasterMixin
from .forms import (FormLocationStepOne, FormMasterStepTwo,
                    ChoiceTypeUser, FormStudentStepThree, FormGyms, ManagementForm)

from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.conf import settings
from formtools.wizard.views import SessionWizardView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.views.generic import TemplateView, DetailView, ListView, CreateView, DeleteView
from django.views.generic.edit import UpdateView


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
            context['professions'] = [master[0].profession.choices.get(int(index)) for index in master[0].profession]
            context['info_prof'] = master[0]
            context['type_user'] = 'Master'
        elif student:
            context['favorite_sport'] = [student[0].favorite_sport.choices.get(int(index)) for index in student[0].favorite_sport]
            context['info_prof'] = student[0]
            context['type_user'] = 'Student'
        context.update(kwargs)
        return super().get_context_data(**context)


class UpdateProfile(LoginRequiredMixin, CheckNotCompleteProfileMixin, UpdateView):
    model = MyUser
    login_url = 'login'
    template_name = 'gyms/update_profile.html'

    def get_form(self, form_class=None):
        user = self.request.user
        if user.type_user == 'M':
            master_data = Master.objects.filter(user=user).values()[0]
            obj_form = FormMasterStepTwo(initial=master_data)
            return obj_form
        elif user.type_user == 'S':
            student_data = Student.objects.filter(user=user).values()[0]
            obj_form_student = FormStudentStepThree(initial=student_data)
            return obj_form_student

    def get_context_data(self, **kwargs):
        user = self.request.user
        obj_form_user = FormRegisterUser(initial={'email': user.email, 'username': user.username})
        kwargs['form_user'] = obj_form_user

        if "form" not in kwargs:
            kwargs["form"] = self.get_form()
        if user.type_user == 'M':
            data_location = {'name_city': user.master.location.name_city, 'province': user.master.location.province}
            obj_form_location = FormLocationStepOne(initial=data_location)
            kwargs['location'] = obj_form_location
            kwargs['profession'] = [int(num_sport) for num_sport in user.master.profession]
        elif user.type_user == 'S':
            data_location = {'name_city': user.student.location.name_city, 'province': user.student.location.province}
            obj_form_location = FormLocationStepOne(initial=data_location)
            kwargs['location'] = obj_form_location
            kwargs['favorite_sport'] = [int(num_sport) for num_sport in user.student.favorite_sport]
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        user, form = request.user, None
        data = request.POST.copy()
        data_location = {'province': data.get('province'), 'name_city': data.get('name_city').title()}
        # check data user !
        if MyUser.objects.filter(email=data.get('email')).exists() and user.email != data.get('email'):
            messages.error(request, 'This email exists !')
            return redirect('update_profile', pk=self.request.user.pk)
        elif MyUser.objects.filter(username=data.get('username')).exists() and user.username != data.get('username'):
            messages.error(request, 'This username exists !')
            return redirect('update_profile', pk=self.request.user.pk)
        data_user = {'email': data.get('email'), 'username': data.get('username')}
        data_files = request.FILES.copy()
        if user.type_user == 'M':
            data['image_person'] = user.master.image_person
            # data files
            if not data_files:
                data_files['image_person'] = user.master.image_person
            # object form master
            form = FormMasterStepTwo(data, data_files)
            # update my object profile master
            if form.is_valid():
                data_master = form.cleaned_data
                MyUser.objects.filter(id=user.id).update(**data_user)
                obj_loc, created = Locations.objects.get_or_create(**data_location)
                data_master['location'] = obj_loc
                Master.objects.update_or_create(id=user.master.id, defaults=data_master)
                messages.success(request, 'your profile updated .')
                return redirect('profile')
        elif user.type_user == 'S':
            # data files
            if not data_files:
                data_files['image_person'] = user.student.image_person
            # object form student
            form = FormStudentStepThree(data, data_files)
            # update my object profile student
            if form.is_valid():
                data_student = form.cleaned_data
                MyUser.objects.filter(id=user.id).update(**data_user)
                obj_loc, created = Locations.objects.get_or_create(**data_location)
                data_student['location'] = obj_loc
                Student.objects.update_or_create(id=user.student.id, defaults=data_student)
                messages.success(request, 'your profile updated .')
                return redirect('profile')
        # error form if exists
        if form.errors:
            error_message = show_first_error(form.errors)
            messages.error(request, f"{error_message.get('field')}:  {error_message.get('text').lstrip('*')}")
            return redirect('update_profile', pk=self.request.user.pk)


class CreateGym(LoginRequiredMixin, CheckUserMasterMixin, CreateView):
    model = Gyms
    login_url = 'login'
    form_class = FormGyms
    template_name = 'gyms/create_gym.html'

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.POST.copy()
        form = FormGyms(data)
        if form.is_valid():
            data_confirm = form.cleaned_data
            data_confirm['master'] = user.master
            Gyms.objects.create(**data_confirm)
            message = 'Gym Successfully Created !'
            messages.success(request, message)
            return redirect('create_gym')
        message = show_first_error(form.errors)
        messages.error(request, f'{message.get("field")} : {message.get("text").lstrip("*")}')
        return redirect('create_gym')


class AllGyms(ListView):
    model = Gyms
    template_name = 'gyms/show_gyms.html'
    context_object_name = 'gyms'

    def get_queryset(self):
        data = self.request.GET
        num_page = data.get('page') or None
        locations = Locations.PROVINCE_CHOICE
        fields = FIELD_SPORTS_CHOICE
        q = Q()
        query_set = Gyms.objects.all()
        self.paginate_by = 24
        name_gym = data.get('name') or None
        province_gym, name_city_gym = data.get('province') or None, data.get('name_city') or None
        field_gym = data.get('field') or None

        if province_gym is not None:
            for code, name_province in locations:
                if province_gym.title() == name_province:
                    province_gym = code
                    q &= Q(location__province=province_gym)
                    break
            if province_gym == data.get('province'):
                province_gym = '0'

        if field_gym is not None:
            for code, name in fields:
                if field_gym.title() == name:
                    field_gym = int(code)
                    q &= Q(field_sport_gym=field_gym)
                    break
            if field_gym == data.get('field'):
                field_gym = '0'

        if name_city_gym is not None:
            name_city_gym = name_city_gym.title()
            q &= Q(location__name_city=name_city_gym)

        if name_gym is not None:
            q &= Q(name__icontains=name_gym)

        if name_gym or province_gym or name_city_gym or field_gym:
            self.paginate_by = None
            query_set = Gyms.objects.filter(q)
        if (name_gym is None) and (name_city_gym is None):
            if (province_gym == '0') or (field_gym == '0'):
                self.paginate_by = None
                query_set = None
        return query_set


class InformationGym(LoginRequiredMixin, DetailView):
    login_url = 'login'
    model = Gyms
    template_name = 'gyms/info_gym.html'
    context_object_name = 'gym'


class ListGymsMaster(LoginRequiredMixin, CheckUserMasterMixin, ListView):
    login_url = 'login'
    model = Gyms
    template_name = 'gyms/gym_master.html'
    context_object_name = 'gyms'

    def get_queryset(self):
        master = self.request.user.master
        query_gym = Gyms.objects.filter(master=master)
        return query_gym


class DeleteGymMaster(LoginRequiredMixin, CheckGymMasterMixin, DeleteView):
    login_url = 'login'
    model = Gyms

    def get(self, request, *args, **kwargs):
        confirm_delete = request.GET.get('result')
        if confirm_delete == 'true':
            pk_gym = kwargs.get('pk')
            gym = Gyms.objects.get(pk=pk_gym)
            name_gym = gym.name
            gym.delete()
            messages.success(request, f'Successfully Delete your Gym {name_gym} .')
            return redirect('gyms_master')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class UpdateGymMaster(LoginRequiredMixin, CheckGymMasterMixin, UpdateView):
    login_url = 'login'
    model = Gyms
    template_name = 'gyms/update_gym.html'

    def get_form(self, form_class=None):
        data_gym = Gyms.objects.filter(pk=self.kwargs.get('pk')).values()[0]
        form_obj = FormGyms(initial=data_gym)
        return form_obj

    def get_context_data(self, **kwargs):
        context = dict()
        context['form'] = self.get_form()
        gym = Gyms.objects.filter(pk=self.kwargs.get('pk'))[0]
        context['location'] = gym.location
        context['days_work'] = gym.get_days_work_list()
        context['time'] = {'time_start': gym.time_start_working.strftime('%H:%M'),
                           'time_end': gym.time_end_working.strftime('%H:%M')}
        return context

    def post(self, request, *args, **kwargs):
        data = request.POST.copy()
        print(len(data['name']))
        obj_location = Locations.objects.get(pk=data.get('location'))
        data['location'] = obj_location
        data['name'] = f'{data.get("name")}  NEW'

        form_obj = FormGyms(data)
        if form_obj.is_valid():
            form_confirm = form_obj.cleaned_data
            form_confirm['name'] = form_confirm.get('name').rstrip('  NEW')
            Gyms.objects.update_or_create(id=kwargs.get('pk'), defaults=form_confirm)
            messages.success(request, f'Successfully Update Gym {form_confirm.get("name")}')
            return redirect('gyms_master')
        message = show_first_error(form_obj.errors)
        messages.error(request, f'{message.get("field")} : {message.get("text").lstrip("*")}')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])



