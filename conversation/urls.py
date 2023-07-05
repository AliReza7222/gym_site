from django.urls import path

from .views import CreateNotification, ListNotification

urlpatterns = [
    path('create_note/', CreateNotification.as_view(), name='create_note'),
    path('list_notifications/<uuid:gym_pk>/', ListNotification.as_view(), name='list_note')
]
