from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from .views import (Home, About, ProfileUser, ShowProfile, UpdateProfile, CreateGym,
                    AllGyms, InformationGym, ListGymsMaster, DeleteGymMaster, UpdateGymMaster,
                    RegisterStudentGym, SendInfoGym, RegisteredGymStudent, StudentsGyms, DeleteStudentsOfGym,
                    RemoveAllStudents, RecordBlockStudent, UnBlockStudent)


urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('about/', About.as_view(), name='about'),
    path('profile/', ProfileUser.as_view(), name='profile'),
    path('show_profile/<uuid:pk>/', ShowProfile.as_view(), name='show_profile'),
    path('update_profile/<uuid:pk>/', UpdateProfile.as_view(), name='update_profile'),
    path('create_gym/', CreateGym.as_view(), name='create_gym'),
    path('all_gyms/', AllGyms.as_view(), name='all_gyms'),
    path('info_gym/<uuid:pk>/', InformationGym.as_view(), name='info_gym'),
    path('gym_master/', ListGymsMaster.as_view(), name='gyms_master'),
    path('delete_gym/<uuid:pk>/', DeleteGymMaster.as_view(), name='delete_gym'),
    path('update_gym/<uuid:pk>/', UpdateGymMaster.as_view(), name='update_gym'),
    path('register_gym/<uuid:pk>/', RegisterStudentGym.as_view(), name='register_gym'),
    path('get_gym_info/<uuid:pk>/', SendInfoGym.as_view(), name='get_gym_info'),
    path('registered_gyms/', RegisteredGymStudent.as_view(), name='registered_gyms'),
    path('students_gym/<uuid:pk>/', StudentsGyms.as_view(), name='students_gym'),
    path('remove_student/<uuid:pk_s>/<uuid:pk_g>/', DeleteStudentsOfGym.as_view(), name='remove_student'),
    path('remove_all_students/<uuid:pk_g>/', RemoveAllStudents.as_view(), name='remove_all_students'),
    path('black_list_gym/<uuid:pk>/', RecordBlockStudent.as_view(), name='black_list'),
    path('un_block_student/<uuid:pk>/<str:user>/', UnBlockStudent.as_view(), name='unblock'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
