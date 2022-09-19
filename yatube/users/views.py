from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.forms import (
    PasswordChangeForm, PasswordResetForm,
    SetPasswordForm
)
from django.contrib.auth.views import (
    PasswordChangeView, PasswordResetView,
    PasswordResetConfirmView
)

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PassChange(PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = 'users/password_change_form.html'
    success_url = reverse_lazy('users:password_change_done')


class PassReset(PasswordResetView):
    form_class = PasswordResetForm
    template_name = 'users/password_reset_form.html'
    success_url = reverse_lazy('users:password_reset_done')


class NewPassReset(PasswordResetConfirmView):
    form_class = SetPasswordForm
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_complete')
