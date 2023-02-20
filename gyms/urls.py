from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from .views import Home, About, ProfileUser, ShowProfile


urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('about/', About.as_view(), name='about'),
    path('profile/', ProfileUser.as_view(), name='profile'),
    path('show_profile/', ShowProfile.as_view(), name='show_profile')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
