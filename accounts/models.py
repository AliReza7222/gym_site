import uuid
from .validations import check_password
from django.db import models
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    TYPE_USR_CHOICE = [
        ('M', "Master"),
        ('S', "Student")
    ]
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=15, validators=[check_password])
    type_user = models.CharField(max_length=1, choices=TYPE_USR_CHOICE)

    def __str__(self):
        return self.username
