import uuid
from .validations import check_password
from django.db import models
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=15, validators=[check_password])

    def __str__(self):
        return self.username
