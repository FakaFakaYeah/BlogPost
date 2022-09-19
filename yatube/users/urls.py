from django.contrib.auth.views import (
    LoginView, LogoutView,
    PasswordChangeDoneView, PasswordResetDoneView,
    PasswordResetCompleteView
)
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'password_change/',
        views.PassChange.as_view(),
        name='password_change'
    ),
    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view
        (template_name='users/password_change_done.html'),
        name='password_change_done'
    ),
    path(
        'password_reset/',
        views.PassReset.as_view(),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        PasswordResetDoneView.as_view
        (template_name='users/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        views.NewPassReset.as_view(),
        name='password_reset_token'
    ),
    path(
        'reset/done/',
        PasswordResetCompleteView.as_view
        (template_name='users/password_reset_complete.html'),
        name='password_complete'
    ),
]
