from django.contrib import admin

from .models import Gyms, Master, Locations, Student, BlockStudent, TimeRegisterInGym


admin.site.register(Gyms)
admin.site.register(Master)
admin.site.register(Locations)
admin.site.register(BlockStudent)
admin.site.register(TimeRegisterInGym)


@admin.register(Student)
class StudentAdminPanel(admin.ModelAdmin):
    filter_horizontal = ['gyms']
