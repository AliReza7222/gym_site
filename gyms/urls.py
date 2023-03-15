from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from .views import Home, About, ProfileUser, ShowProfile, \
    UpdateProfile, CreateGym, AllGyms, InformationGym, ListGymsMaster, DeleteGymMaster, UpdateGymMaster


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
    path('update_gym/<uuid:pk>/', UpdateGymMaster.as_view(), name='update_gym')

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
