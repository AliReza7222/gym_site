import re

from django.core.validators import ValidationError


def true_phone_number(value):
    get_num = re.findall('09[0-9]{9}', value)
    if len(get_num) == 1:
        number = get_num[0]
        if len(number) == 11 and number == value:
            return value
    raise ValidationError('number phone must be contain 11 number and start with 09 .')


def check_national_code(value):
    get_national_code = re.findall('[0-9]{10}', value)
    if len(get_national_code) == 1:
        code_national = get_national_code[0]
        if code_national == value:
            return value
    raise ValidationError('Enter a number nationality True contain numbers')


def check_exists_code_national(value):
    num_check = value[:9][::-1]
    sum_nums = 0
    for index_num, num in enumerate(num_check, start=2):
        sum_nums += (int(num) * index_num)
    remains = sum_nums % 11
    if (remains < 2) and (value[-1] != remains):
        raise ValidationError('The entered national code is not correct .')
    last_num_value = 11 - remains
    if (remains >= 2) and (int(value[-1]) != last_num_value):
        raise ValidationError('The entered national code is not correct .')
    return value




def get_words(value):
    get_input = re.findall('[a-zA-Z\s]+', value)
    if len(get_input) == 1:
        input_words = get_input[0]
        if value == input_words:
            return input_words
    raise ValidationError('this field be must contain words .')