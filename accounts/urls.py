from django.urls import path

from .views import RegisterUser, LoginUser, ChangePassword, LogoutUser, ChangePasswordWithUser


urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('change_password/', ChangePassword.as_view(), name='change_password'),
    path('logout/', LogoutUser.as_view(), name='logout'),
    path('change_password_with_user/', ChangePasswordWithUser.as_view(), name='change_password_with_user'),
]
