from django.contrib import admin

from .models import Gyms, Master, Locations, Student


admin.site.register(Gyms)
admin.site.register(Master)
admin.site.register(Locations)


@admin.register(Student)
class StudentAdminPanel(admin.ModelAdmin):
    filter_horizontal = ['gyms']
