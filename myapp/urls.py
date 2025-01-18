from django.urls import path
from . import views

urlpatterns = [
    path('', views.signup, name='signup'),  # Default route points to signup
    path('login/', views.login_user, name='login'),  # Login page
    path('dashboard/', views.dashboard, name='dashboard'), 
    path('logout/', views.logout_user, name='logout'),
]