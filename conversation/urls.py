from django.urls import path

from .views import CreateNotification, ListNotification, ListNotificationsCreatedMaster, RemoveNotification

urlpatterns = [
    path('create_note/', CreateNotification.as_view(), name='create_note'),
    path('list_notifications/<uuid:gym_pk>/', ListNotification.as_view(), name='list_note'),
    path('note_created_master/', ListNotificationsCreatedMaster.as_view(), name='note_master'),
    path('remove_note/<slug:note_pk>/', RemoveNotification.as_view(), name='remove_note')
]
