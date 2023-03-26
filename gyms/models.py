import os.path
import uuid

from .validations import true_phone_number, check_national_code, get_words, check_exists_code_national

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from multiselectfield import MultiSelectField
from django.core.exceptions import ValidationError
from accounts.models import MyUser


FIELD_SPORTS_CHOICE = [
    (1, 'Football'),
    (2, 'Volleyball'),
    (3, 'Swim'),
    (4, 'Basketball'),
    (5, 'Tennis'),
    (6, 'Table Tennis'),
    (7, 'Baseball'),
    (8, 'Golf'),
    (9, 'Wrestling'),
    (10, "Bodybuilding"),
    (11, "Boxing"),
    (12, "Kung Fu"),
    (13, "Karate"),
    (14, "MMA"),
    (15, "shooting"),
    (16, "Jujitsu"),
    (17, "taekwondo"),
    (18, "water polo"),
    (19, "Running"),
    (20, "Mountaineering"),
    (21, "Field hockey"),
    (22, "bowling"),
    (23, "handball"),
    (24, "American football"),
    (25, "futsal"),

]


class Locations(models.Model):
    PROVINCE_CHOICE = [
        ("1", "Alborz"),
        ('2', "Ardabil"),
        ('3', "East Azerbaijan"),
        ('4', "West Azerbaijan"),
        ('5', "Bushehr"),
        ('6', "Chahar Mahaal and Bakhtiari"),
        ('7', "Fars"),
        ('8', "Gilan"),
        ('9', "Golestan"),
        ('10', "Hamadan"),
        ('11', "Hormozgan"),
        ('12', "Ilam"),
        ('13', "Isfahan"),
        ('14', "Kerman"),
        ('15', "Kermanshah"),
        ('16', "North Khorasan"),
        ('17', "Razavi Khorasan"),
        ('18', "South Khorasan"),
        ('19', "Khuzestan"),
        ('20', "Kohgiluyeh and Boyer-Ahmad"),
        ('21', "Kurdistan"),
        ('22', "Lorestan"),
        ('23', "Markazi"),
        ('24', "Mazandaran"),
        ('25', "Qazvin"),
        ('26', "Qom"),
        ('27', "Semnan"),
        ('28', "Sistan and Baluchestan"),
        ('29', "Tehran"),
        ('30', "Yazd"),
        ('31', "Zanjan"),
    ]
    id = models.UUIDField(editable=False, primary_key=True, default=uuid.uuid4)
    province = models.CharField(max_length=2, choices=PROVINCE_CHOICE)
    name_city = models.CharField(max_length=100)

    def __str__(self):
        address = f'{self.get_province_display()}/{self.name_city}'
        return address


class Master(models.Model):
    Gender = [
        ('M', 'Male'),
        ('F', 'Female')
    ]
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, validators=[get_words])
    last_name = models.CharField(max_length=50, validators=[get_words])
    age = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(200)])
    location = models.ForeignKey(Locations, on_delete=models.CASCADE)
    gender = models.CharField(max_length=1, choices=Gender)
    number_phone = models.CharField(max_length=11, validators=[true_phone_number])
    image_person = models.ImageField(upload_to='image/')
    national_code = models.CharField(max_length=10, validators=[check_national_code, check_exists_code_national])
    salary = models.PositiveIntegerField(default=0, editable=False)
    profession = MultiSelectField(choices=FIELD_SPORTS_CHOICE, max_choices=100, max_length=100)

    def delete(self, using=None, keep_parents=False):
        self.image_person.storage.delete(str(self.image_person.name))
        super().delete()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Gyms(models.Model):

    GENDER_CHOICE = [
        ('m', "Male"),
        ('f', "Female"),
        ('fm', "Female & Male")
    ]
    DAYS_CHOICE = [
        ("1", "Saturday"),
        ("2", "Sunday"),
        ("3", "Monday"),
        ("4", "Tuesday"),
        ("5", "Wednesday"),
        ("6", "Thursday"),
        ("7", "Friday"),
    ]
    STATE_GYM = [
        (1, 'have capacity'),
        (2, "full capacity")
    ]
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=50, validators=[get_words])
    gender = models.CharField(max_length=2, choices=GENDER_CHOICE)
    location = models.ForeignKey(Locations, on_delete=models.CASCADE)
    field_sport_gym = models.IntegerField(choices=FIELD_SPORTS_CHOICE)
    days_work = MultiSelectField(choices=DAYS_CHOICE, max_choices=100, max_length=100)
    time_start_working = models.TimeField()
    time_end_working = models.TimeField()
    capacity_gym = models.PositiveIntegerField()
    state = models.IntegerField(choices=STATE_GYM, default=1)
    number_register_person = models.PositiveIntegerField(default=0)
    master = models.ForeignKey(Master, on_delete=models.CASCADE)
    monthly_tuition = models.PositiveIntegerField()
    address_exact = models.TextField()

    def master_gym(self, user):
        self.master = user
        self.save()

    def register_person(self, user):
        capacity = self.capacity_gym
        num_register = len(self.student_set.all())
        if capacity == num_register:
            self.state = 2
            self.save()
            return 0, 'full capacity'

        elif int(capacity) > num_register and self.state != 2:
            self.number_register_person = num_register + 1
            self.student_set.add(user)
            if self.number_register_person == self.capacity_gym:
                self.state = 2
            self.save()
            return 1, f'register {user}'

        elif self.state == 2:
            return 0, 'full capacity'

    def __str__(self):
        return f'{self.name}/({self.time_start_working})-({self.time_end_working})/{self.get_field_sport_gym_display()}'


class Student(models.Model):
    GENDER_CHOICE = [
        ('M', 'Male'),
        ('F', 'Female')
    ]
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, validators=[get_words])
    last_name = models.CharField(max_length=50, validators=[get_words])
    gender = models.CharField(choices=GENDER_CHOICE, max_length=1)
    location = models.ForeignKey(Locations, on_delete=models.CASCADE)
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(200)])
    image_person = models.ImageField(upload_to='image/')
    national_code = models.CharField(max_length=10, validators=[check_national_code, check_exists_code_national])
    number_phone = models.CharField(max_length=11, validators=[true_phone_number])
    gyms = models.ManyToManyField(Gyms, blank=True)
    favorite_sport = MultiSelectField(choices=FIELD_SPORTS_CHOICE, max_choices=100, max_length=100)
    credit = models.PositiveIntegerField(default=0, editable=False)

    def delete(self, using=None, keep_parents=False):
        self.image_person.storage.delete(str(self.image_person.name))
        super().delete()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
