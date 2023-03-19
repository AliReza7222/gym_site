from django.contrib import messages
from django.shortcuts import redirect


# create a mixin for check user is student
class CheckUserStudentMixin:

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.type_user != 'S':
            messages.error(request, "You Can't Enter This Page !")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class CheckUserMasterMixin:

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.type_user != 'M':
            messages.error(request, "You Can't Enter This Page !")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)