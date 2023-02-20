from django.http import HttpResponse
from django.shortcuts import redirect


# This file is for create mixin custom

class CheckCompleteProfileMixin:

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.type_user:
            return super().dispatch(request, *args, **kwargs)
        return redirect('show_profile')
