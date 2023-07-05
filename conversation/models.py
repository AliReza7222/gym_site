from django.db import models

from gyms.validations import get_words
from gyms.models import Student, Master, Gyms


class Question(models.Model):
    student_user = models.ForeignKey(Student, on_delete=models.CASCADE)
    topic = models.CharField(max_length=250, validators=[get_words])
    name_gym = models.CharField(max_length=150, validators=[get_words])
    question = models.TextField()
    time_question = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = [
            ('topic', 'student_user', 'time_question')
        ]


class Answer(models.Model):
    master_user = models.ForeignKey(Master, on_delete=models.CASCADE)
    topic = models.CharField(max_length=250, validators=[get_words])
    name_gym = models.CharField(max_length=150, validators=[get_words])
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()
    time_answer = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = [
            ('topic', 'master_user', 'time_answer')
        ]


class Notification(models.Model):
    gym = models.ForeignKey(Gyms, on_delete=models.CASCADE)
    message = models.TextField()
    topic = models.CharField(max_length=150, validators=[get_words])
    time_notification = models.DateTimeField(auto_now=True)
    master = models.ForeignKey(Master, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.topic}/{self.message[:20]}.....'

    class Meta:
        index_together = [
            ('gym', 'topic', 'time_notification')
        ]
