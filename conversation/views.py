from django.shortcuts import render
from django.http import  Http404
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, ListView

from .models import Notification
from .forms import NotificationForm
from gyms.mixins import CheckUserMasterMixin, StudentCheckUserMixin, ExistsNotificationCheckMixin
from gyms.models import Gyms


def return_type_info_note(student):
    try:
        type_new_notification = type(eval(student.new_notification))
    except:
        type_new_notification = str

    return type_new_notification


class ListNotification(LoginRequiredMixin, StudentCheckUserMixin, ExistsNotificationCheckMixin, ListView):
    login_url = 'login'
    model = Notification
    template_name = 'conversation/list_notifications.html'
    context_object_name = 'notifications'
    paginate_by = 14

    def get(self, request, *args, **kwargs):
        user = request.user.student
        type_new_notification = return_type_info_note(user)
        if type_new_notification == list:
            name_gym = eval(user.new_notification)[1]
            gym = Gyms.objects.get(pk=kwargs.get('gym_pk'))
            if name_gym == gym.name:
                user.new_notification = '0'
                user.save()
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        if not allow_empty:
            if self.get_paginate_by(self.object_list) is not None and hasattr(
                    self.object_list, "exists"
            ):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(
                    ("Empty list and “%(class_name)s.allow_empty” is False.")
                    % {
                        "class_name": self.__class__.__name__,
                    }
                )
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_queryset(self):
        gym = Gyms.objects.get(pk=self.kwargs['gym_pk'])
        queryset = gym.notification_set.all()
        return queryset


class CreateNotification(LoginRequiredMixin, CheckUserMasterMixin, CreateView):
    login_url = 'login'
    model = Notification
    form_class = NotificationForm
    template_name = 'conversation/notification_page.html'

    def get(self, request, *args, **kwargs):
        self.object = None
        user = request.user.master
        gyms = {'gyms': Gyms.objects.filter(master=user)}
        self.extra_context = gyms
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = request.POST
        gym = Gyms.objects.get(pk=data.get('gym'))
        notification_data = {'topic': data.get('topic'),
                             'message': data.get('message'), 'master': request.user.master,
                             'gym': gym
                             }
        note = Notification.objects.create(**notification_data)
        messages.success(request, f'The notification {note} was sent successfully.')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
