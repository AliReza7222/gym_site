import uuid

from django.db import models

from gyms.validations import get_words
from gyms.models import Student, Master, Gyms


class Notification(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False
    )
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
