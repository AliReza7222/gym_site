from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from .views import Home, About, ProfileUser


urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('about/', About.as_view(), name='about'),
    path('profile/', ProfileUser.as_view(), name='profile')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
