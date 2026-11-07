from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import StyledAuthenticationForm
from .views import profile_view, signup_view
from .farm_views import farm_activate, farm_delete, farm_detail, farm_edit, farm_list

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html', authentication_form=StyledAuthenticationForm, redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('signup/', signup_view, name='signup'),
    path('profile/', profile_view, name='profile'),
    path('farms/', farm_list, name='farms'),
    path('farms/<int:pk>/', farm_detail, name='farm_detail'),
    path('farms/<int:pk>/edit/', farm_edit, name='farm_edit'),
    path('farms/<int:pk>/delete/', farm_delete, name='farm_delete'),
    path('farms/<int:pk>/activate/', farm_activate, name='farm_activate'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html', email_template_name='accounts/password_reset_email.html', success_url='/accounts/password-reset/done/'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html', success_url='/accounts/reset/done/'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
]
