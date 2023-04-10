import os.path

from accounts.views import show_first_error
from .validations import get_words
from .utils import create_location
from accounts.forms import FormRegisterUser
from .models import Locations, Master, Student, MyUser, Gyms, FIELD_SPORTS_CHOICE, TimeRegisterInGym, BlockStudent
from .mixins import (CheckCompleteProfileMixin, CheckNotCompleteProfileMixin, CheckUserMasterMixin, CheckGymMasterMixin,
                     RegisterStudentMixin, StudentCheckUserMixin)
from .forms import (FormLocationStepOne, FormMasterStepTwo,
                    ChoiceTypeUser, FormStudentStepThree, FormGyms, ManagementForm)

from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse, Http404, HttpResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.conf import settings
from formtools.wizard.views import SessionWizardView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.views.generic import TemplateView, DetailView, ListView, CreateView, DeleteView, RedirectView, FormView
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

    def get(self, request, *args, **kwargs):
        if len(Locations.objects.all()) == 0:
            create_location()
        self.storage.reset()
        # reset the current step to the first step.
        self.storage.current_step = self.steps.first
        return self.render(self.get_form())

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
                if not Locations.objects.filter(province=clean_data.get('province'), name_city=clean_data.get('name_city')).exists:
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
        province = Locations.PROVINCE_CHOICE
        data_location['province'] = province[int(data_location.get('province')) - 1][1]
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
            name, location_gym = data_confirm.get('name').title(), data_confirm.get('location')
            if Gyms.objects.filter(name=name, location=location_gym).exists():
                messages.error(request, 'A Gym With Name exists This Location !')
                return HttpResponseRedirect(request.META['HTTP_REFERER'])
            data_confirm['master'] = user.master
            data_confirm['name'] = name
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
                    q &= Q(location__province=name_province)
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

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        user = request.user
        if user.is_authenticated and user.type_user == 'S':
            student = user.student
            self.extra_context = {"gyms_student": student.gyms.all()}
        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(
                    self.object_list, "exists"
            ):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(
                    "Empty list and “%(class_name)s.allow_empty” is False."
                    % {
                        "class_name": self.__class__.__name__,
                    }
                )
        context = self.get_context_data()
        return self.render_to_response(context)


class InformationGym(LoginRequiredMixin, DetailView):
    login_url = 'login'
    model = Gyms
    template_name = 'gyms/info_gym.html'
    context_object_name = 'gym'

    def split_number(self, value):
        value = str(value)
        answer_num = ''
        if len(value) <= 3:
            return value
        for index_word, num in enumerate(value[::-1], start=1):
            answer_num += num
            if index_word % 3 == 0 and len(value) != index_word:
                answer_num += ','
        return answer_num[::-1]

    def get_context_data(self, **kwargs):
        context = {}
        if self.object:
            context["object"] = self.object
            number_split = self.split_number(self.object.monthly_tuition)
            context['monthly_tuition'] = number_split
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        context.update(kwargs)
        return super().get_context_data(**context)


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
            if len(gym.student_set.all()) > 0:
                messages.error(request, 'You cannot delete this gym because students are registered in this gym.')
                return HttpResponseRedirect(request.META['HTTP_REFERER'])
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
        gym = Gyms.objects.get(pk=kwargs.get('pk'))
        obj_location = Locations.objects.get(pk=data.get('location'))
        data['location'] = obj_location
        form_obj = FormGyms(data)

        if form_obj.is_valid():
            form_confirm = form_obj.cleaned_data
            name = form_confirm.get('name').title()
            form_confirm['name'] = name
            if gym.name != name and Gyms.objects.filter(name=name, location=obj_location):
                messages.error(request, 'A Gym With Name Exists This Location !')
                return HttpResponseRedirect(request.META['HTTP_REFERER'])
            Gyms.objects.update_or_create(id=kwargs.get('pk'), defaults=form_confirm)
            messages.success(request, f'Successfully Update Gym {form_confirm.get("name")}')
            return redirect('gyms_master')
        message = show_first_error(form_obj.errors)
        messages.error(request, f'{message.get("field")} : {message.get("text").lstrip("*")}')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class SendInfoGym(LoginRequiredMixin, RegisterStudentMixin, RedirectView):
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        pk_gym = kwargs.get('pk')
        gym = Gyms.objects.get(pk=pk_gym)
        info = {
            'monthly_tuition': gym.monthly_tuition,
            'gender': gym.get_gender_display(),
            'time_start_working': gym.time_start_working,
            'time_end_working': gym.time_end_working,
        }
        return JsonResponse(info)


class RegisterStudentGym(LoginRequiredMixin, RegisterStudentMixin, UpdateView):
    login_url = 'login'
    redirect_field_name = 'all_gyms'
    model = Gyms

    def get(self, request, *args, **kwargs):
        user = request.user
        gym = Gyms.objects.get(id=kwargs.get('pk'))
        master_gym, tuition_gym = gym.master, gym.monthly_tuition
        black_list = gym.blockstudent_set.values_list('email_student', flat=True)
        student = user.student
        if user.email in black_list:
            message = 'You cannot register in this gym because you are blocked by the master.'
            messages.error(request, message)
            return redirect('all_gyms')
        elif student in gym.student_set.all():
            messages.error(request, 'You are already registered in this gym.')
            return redirect('all_gyms')
        elif student.credit < tuition_gym:
            messages.error(request, 'The money in your account is less than the Gym tuition.')
            return redirect('all_gyms')
        elif gym.state == 2 or gym.capacity_gym == gym.number_register_person:
            messages.error(request, 'This Gym Full Capacity .')
            return redirect('all_gyms')
        elif student.credit >= tuition_gym:
            master_gym.salary += tuition_gym
            student.credit -= tuition_gym
            register_student = gym.register_person(student)
            if register_student[0]:
                master_gym.save()
                student.save()
                message = f'You successfully register This Gym \"{gym.name}\"'
                messages.success(request, message)
                return redirect('all_gyms')


class RegisteredGymStudent(LoginRequiredMixin, StudentCheckUserMixin, ListView):
    login_url = 'login'
    model = Gyms
    template_name = 'gyms/gyms_student.html'

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        student = request.user.student
        gyms_student = student.gyms.all()
        if not gyms_student:
            messages.error(request, "you don't register any gyms .")
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        self.extra_context = {'gyms': gyms_student}

        allow_empty = self.get_allow_empty()
        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(
                    self.object_list, "exists"
            ):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(
                    "Empty list and “%(class_name)s.allow_empty” is False."
                    % {
                        "class_name": self.__class__.__name__,
                    }
                )
        context = self.get_context_data()
        return self.render_to_response(context)


class StudentsGyms(LoginRequiredMixin, CheckUserMasterMixin, ListView):
    login_url = 'login'
    model = Student
    template_name = 'gyms/student_gym.html'
    context_object_name = 'students_gym'
    paginate_by = 25

    def students_gym(self):
        gym = Gyms.objects.get(id=self.kwargs.get('pk'))
        students_gym = gym.student_set.all()
        return students_gym, gym

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        if len(self.students_gym()[0]) == 0:
            messages.error(request, 'No one has registered in this Gym.')
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        self.extra_context = {'gym': self.students_gym()[1]}
        allow_empty = self.get_allow_empty()
        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(
                    self.object_list, "exists"
            ):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(
                    "Empty list and “%(class_name)s.allow_empty” is False."
                    % {
                        "class_name": self.__class__.__name__,
                    }
                )
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_queryset(self):
        data = self.request.GET
        students_gym = self.students_gym()[0]
        number_student = [str(index_student) for index_student in range(1, len(students_gym) + 1)]
        query_set = list(zip(number_student, students_gym))
        student_name, student_email = data.get('name'), data.get('email')
        student_phone_number, student_age = data.get('phone_number'), data.get('age')
        q = Q()

        if student_name:
            q &= (Q(first_name__icontains=student_name) | Q(last_name__icontains=student_name))
        if student_email:
            student_email = student_email.strip().strip('%09').replace('%40', '@')
            q &= Q(user__email=student_email)
        if student_age:
            q &= Q(age=student_age)
        if student_phone_number:
            q &= Q(number_phone=student_phone_number)

        if student_age or student_name or student_email or student_phone_number:
            students_desired = Student.objects.filter(q, gyms__in=[self.students_gym()[1]])
            number_student = [str(student_index) for student_index in range(1, len(students_desired) + 1)]
            query_set = list(zip(number_student, students_desired))
            self.paginate_by = None

        return query_set


class DeleteStudentsOfGym(LoginRequiredMixin, CheckUserMasterMixin, DeleteView):
    login_url = 'login'
    model = Gyms

    def get(self, request, *args, **kwargs):
        result = request.GET.get('result')
        if result == 'true':
            gym = Gyms.objects.get(id=kwargs.get('pk_g'))
            student = Student.objects.get(id=kwargs.get('pk_s'))
            time_register = TimeRegisterInGym.objects.get(gym_id=gym.id, student_email=student.user.email)
            gym.student_set.remove(student)
            gym.time_register_student.remove(time_register)
            time_register.delete()
            gym.number_register_person -= 1
            if gym.state == 2:
                gym.state = 1
            gym.save()
            if gym.number_register_person == 0:
                messages.success(request,
                                 f'{student.first_name} {student.last_name} was removed from gym and now your gym is empty !')
                return redirect('gyms_master')
            messages.success(request, f'{student.first_name} {student.last_name} removed of gym .')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class RemoveAllStudents(LoginRequiredMixin, CheckUserMasterMixin, DeleteView):
    login_url = 'login'
    model = Gyms

    def get(self, request, *args, **kwargs):
        result = request.GET.get('result')
        if result == 'true':
            gym = Gyms.objects.get(id=kwargs.get('pk_g'))
            if gym.number_register_person == 0:
                messages.error(request, 'No one has registered in this gym !')
                return redirect('gyms_master')
            gym.time_register_student.clear()
            gym.student_set.clear()
            gym.number_register_person = 0
            if gym.state == 2:
                gym.state = 1
            gym.save()
            message = 'Your gym students have all been removed from the gym.'
            messages.success(request, message)
            return redirect('gyms_master')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class RecordBlockStudent(LoginRequiredMixin, CheckUserMasterMixin, CreateView):
    login_url = 'login'
    model = BlockStudent
    template_name = 'gyms/view_block_list.html'
    fields = ['email_student']

    def get(self, request, *args, **kwargs):
        self.object = None
        gym = Gyms.objects.get(id=kwargs.get('pk'))
        black_list = gym.blockstudent_set.values_list('email_student', flat=True)
        self.extra_context = {'gym': gym, "black_list": black_list}
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        email, gym = request.POST.get('email'), Gyms.objects.get(id=kwargs.get('pk'))
        if email:
            BlockStudent.objects.create(email_student=email, gym=gym)
            messages.success(request, 'block successfully .')
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        messages.error(request, 'A Error Exists ...')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
