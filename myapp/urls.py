from django.urls import path
from . import views  # Import your views from the app

urlpatterns = [
    path('', views.home, name='home'),  # Root URL ('/') shows the home view
    path('resume-tailor/', views.resume_tailor, name='resume_tailor'),
]