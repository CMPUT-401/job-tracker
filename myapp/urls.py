from django.urls import path
from . import views

urlpatterns = [
    path('', views.signup, name='signup'),  # Default route points to signup
    path('login/', views.login_user, name='login'),  # Login page
    path('dashboard/', views.dashboard, name='dashboard'), 
    path('add-application/', views.add_application, name='add_application'),
    path('logout/', views.logout_user, name='logout'),
    path('', views.home, name='home'),  # Root URL ('/') shows the home view
    path('resume-tailor/', views.resume_tailor, name='resume_tailor'),
]