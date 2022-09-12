from django.contrib.auth import views as auth_views
from django.urls import path
from users.forms import CustomPasswordResetForm, CustomPasswordResetConfirmForm
from users import views as user_views

urlpatterns = [
    path('profile/', user_views.profile, name='profile'),
    path('profile/<str:username>/', user_views.publicProfile, name='public-profile'),
    path('login/', user_views.login, name='login'),
    path('logout/', user_views.logout, name='logout'),
    path('register/', user_views.register, name='register'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html', form_class=CustomPasswordResetForm), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-complete', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html', form_class=CustomPasswordResetConfirmForm), name='password_reset_confirm'),
]
