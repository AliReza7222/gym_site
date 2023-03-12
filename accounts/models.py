import uuid
from .validations import check_password, UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        "username",
        max_length=20,
        unique=True,
        help_text=(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100, validators=[check_password])
    type_user = models.CharField(max_length=1, null=True, blank=True)

    def __str__(self):
        return self.username
