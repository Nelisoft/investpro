from django.urls import path


from . import views
urlpatterns = [
    path('verify/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('register/', views.Register, name='register'),
    path('login/', views.Login, name='login'),
    
    
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),
    path('reset-password/', views.password_reset_request, name='reset_password'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('reset-password-complete/', views.password_reset_complete, name='password_reset_complete'),
    path('logout/', views.logout_user, name='logout'),
    
    
]
