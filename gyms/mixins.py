from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect, HttpResponseRedirect
from .models import Gyms


# This file is for create mixin custom

class CheckCompleteProfileMixin:

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.type_user:
            return redirect('show_profile', pk=user.pk)

        return super().dispatch(request, *args, **kwargs)


class CheckNotCompleteProfileMixin:

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.type_user:
            return redirect('profile')

        return super().dispatch(request, *args, **kwargs)


class CheckUserMasterMixin:

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.type_user == 'M':
            return super().dispatch(request, *args, **kwargs)
        messages.error(request, 'you don\'t enter to this page !')
        return redirect('home')


class CheckGymMasterMixin:

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        pk_gym = kwargs.get('pk')
        if user.type_user == 'M':
            gym_master = Gyms.objects.filter(master=user.master, id=pk_gym)
            if gym_master:
                return super().dispatch(request, *args, **kwargs)

        messages.error(request, 'you don\'t enter to this page !')
        return redirect('home')


class RegisterStudentMixin:

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.type_user == 'S':
            return super().dispatch(request, *args, **kwargs)
        elif user.type_user == 'M':
            messages.error(request, 'You Can not Register Because You are Not Student !')
            return redirect('all_gyms')


class StudentCheckUserMixin:

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.type_user == 'S':
            return super().dispatch(request, *args, **kwargs)
        messages.error(request, 'You Can Not Enter This Page .')
        return redirect('home')


class ExistsNotificationCheckMixin:

    def dispatch(self, request, *args, **kwargs):
        gym_pk = kwargs.get('gym_pk')
        gym = Gyms.objects.get(pk=gym_pk)
        if gym.notification_set.all().exists():
            return super().dispatch(request, *args, **kwargs)

        message = 'You have no notifications !'
        messages.error(request, message)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
