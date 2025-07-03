from django.urls import path
from userauth import views as userauth_views
from . import views
urlpatterns = [
    path('', views.Home, name='home'),
    path('dashboard/',views.Dashboard, name='dashboard'),
    path('dashboard/deposit/', views.deposit_view, name='user_deposit'),
    path('dashboard/withdraw/', views.withdraw_view, name='withdraw'),
     path('dashboard/profile/', userauth_views.profile, name='profile'),
     path('dashboard/withdrawals/history/', views.withdrawal_history_view, name='withdrawal_history'),
     path('dashboard/deposit-history/', views.deposit_history_view, name='deposit_history'),

]
