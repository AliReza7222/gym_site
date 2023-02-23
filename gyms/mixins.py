from django.http import HttpResponse
from django.shortcuts import redirect


# This file is for create mixin custom

class CheckCompleteProfileMixin:

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.type_user:
            print('show_profile')
            return redirect('show_profile', pk=user.pk)

        return super().dispatch(request, *args, **kwargs)


class CheckNotCompleteProfileMixin:

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.type_user:
            return redirect('profile')

        return super().dispatch(request, *args, **kwargs)