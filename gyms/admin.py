from django.contrib import admin

from .models import Gyms, Master, Locations, Student, BlockStudent


admin.site.register(Gyms)
admin.site.register(Master)
admin.site.register(Locations)
admin.site.register(BlockStudent)


@admin.register(Student)
class StudentAdminPanel(admin.ModelAdmin):
    filter_horizontal = ['gyms']
