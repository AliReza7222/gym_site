import re
from django.core.validators import ValidationError, RegexValidator
from django.utils.deconstruct import deconstructible


def check_password(value):
    get_password = re.findall('[a-zA-Z0-9]+', value)
    if len(get_password) != 1:
        raise ValidationError("password must contain words and numbers ...")
    elif len(get_password) == 1:
        if get_password[0] != value:
            raise ValidationError("password must contain words and numbers ...")
    return value


@deconstructible
class UnicodeUsernameValidator(RegexValidator):
    regex = r"^[\w.@+-]+\Z"
    message = (
        "Enter a valid username. This value may contain only letters, "
        "numbers, and @/./+/-/_ characters."
    )
    flags = 0

