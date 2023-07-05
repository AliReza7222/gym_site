import datetime

from .models import Notification
from gyms.models import Gyms

from django.dispatch import receiver
from django.db.models.signals import post_save


@receiver(post_save, sender=Notification)
def receiver_students(sender, instance, created, **kwargs):
    gym = instance.gym
    students = gym.student_set.all()
    time = instance.time_notification.strftime('%Y-%m-%d %H:%M:%S')
    message = f'you have a new message from gym {instance.gym.name} of master {instance.master} at {time}.'
    for student in students:
        student.new_notification = message
        student.save()


@receiver(post_save, sender=Gyms)
def send_notification_update(sender, instance, created, update_fields, **kwargs):
    if not created:
        info_note = dict()
        info_note['gym'] = instance
        info_note['message'] = f'gym {instance.name} updated information .'
        info_note['topic'] = f'Update information gym {instance.name}'
        info_note['master'] = instance.master
        info_note['time_notification'] = datetime.datetime.now()
        Notification.objects.create(**info_note)

        students = instance.student_set.all()
        for student in students:
            student.new_notification = info_note['message']
            student.save()
