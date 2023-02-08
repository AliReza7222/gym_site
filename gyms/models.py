import uuid

from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import MyUser


class Locations(models.Model):
    PROVINCE_CHOICE = [
        ("A", "Alborz"),
        ("A", "Ardabil"),
        ("E", "East Azerbaijan"),
        ("W", "West Azerbaijan"),
        ("B", "Bushehr"),
        ("C", "Chahar Mahaal and Bakhtiari"),
        ("F", "Fars"),
        ("G", "Gilan"),
        ("G", "Golestan"),
        ("H", "Hamadan"),
        ("H", "Hormozgan"),
        ("I", "Ilam"),
        ("I", "Isfahan"),
        ("K", "Kerman"),
        ("K", "Kermanshah"),
        ("N", "North Khorasan"),
        ("R", "Razavi Khorasan"),
        ("S", "South Khorasan"),
        ("K", "Khuzestan"),
        ("K", "Kohgiluyeh and Boyer-Ahmad"),
        ("K", "Kurdistan"),
        ("L", "Lorestan"),
        ("M", "Markazi"),
        ("M", "Mazandaran"),
        ("Q", "Qazvin"),
        ("Q", "Qom"),
        ("S", "Semnan"),
        ("S", "Sistan and Baluchestan"),
        ("T", "Tehran"),
        ("Y", "Yazd"),
        ("Z", "Zanjan"),
    ]
    id = models.UUIDField(editable=False, primary_key=True, default=uuid.uuid4)
    province = models.CharField(max_length=1, choices=PROVINCE_CHOICE)
    name_city = models.CharField(max_length=100)
    address_exact = models.TextField()

    def __str__(self):
        address = f'{self.get_province_display()}/{self.name_city}'
        return address


class Master(models.Model):
    Gender = [
        ('M', 'Male'),
        ('F', 'Female')
    ]
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.PositiveIntegerField()
    location = models.ForeignKey(Locations, on_delete=models.CASCADE)
    gender = models.CharField(max_length=1, choices=Gender)
    number_phone = models.CharField(max_length=11)
    image_profiles = models.ImageField(upload_to='image_master/')
    national_code = models.CharField(max_length=11)
    credit = models.PositiveIntegerField(default=0, editable=False)

    def delete(self, using=None, keep_parents=False):
        self.image_profiles.storage.delete(str(self.image_profiles.name))
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
        ("S", "Saturday"),
        ("S", "Sunday"),
        ("M", "Monday"),
        ("T", "Tuesday"),
        ("W", "Wednesday"),
        ("T", "Thursday"),
        ("F", "Friday"),
    ]
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
    STATE_GYM = [
        (1, 'have capacity'),
        (2, "full capacity")
    ]
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICE)
    location = models.ForeignKey(Locations, on_delete=models.CASCADE)
    field_sport_gym = models.IntegerField(choices=FIELD_SPORTS_CHOICE)
    days_work = models.CharField(max_length=100, choices=DAYS_CHOICE)
    time_start_working = models.TimeField(unique=True)
    time_end_working = models.TimeField(unique=True)
    capacity_gym = models.PositiveIntegerField()
    state = models.IntegerField(choices=STATE_GYM, default=1)
    number_register_person = models.PositiveIntegerField(default=0)
    master = models.ForeignKey(Master, on_delete=models.CASCADE)
    monthly_tuition = models.PositiveIntegerField()

    def master_gym(self, user):
        self.master = user
        self.save()

    def register_person(self, user):
        capacity = self.capacity_gym
        num_register = self.number_register_person
        if capacity == num_register:
            self.state = 2
            self.save()
            return 0, 'full capacity'

        elif capacity > num_register:
            self.number_register_person += 1
            self.student = user
            self.state = 1
            self.save()
            return 1, f'register {user}'

    def __str__(self):
        return f'{self.name}/({self.time_start_working})-({self.time_end_working})/{self.get_field_sport_gym_display()}'


class Student(models.Model):
    GENDER_CHOICE = [
        ('M', 'Male'),
        ('F', 'Female')
    ]
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(choices=GENDER_CHOICE, max_length=1)
    location = models.ForeignKey(Locations, on_delete=models.CASCADE)
    age = models.PositiveIntegerField()
    image_person = models.ImageField(upload_to='image_student/')
    national_code = models.CharField(max_length=11)
    number_phone = models.CharField(max_length=11)
    gyms = models.ManyToManyField(Gyms, blank=True)
    credit = models.PositiveIntegerField(default=0, editable=False)

    def delete(self, using=None, keep_parents=False):
        self.image_person.storage.delete(str(self.image_person.name))
        super().delete()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
