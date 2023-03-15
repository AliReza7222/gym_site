from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
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
        gym_master = Gyms.objects.filter(master=user.master, id=pk_gym)
        if user.type_user == 'M' and gym_master:
            return super().dispatch(request, *args, **kwargs)

        messages.error(request, 'you don\'t enter to this page !')
        return redirect('home')
