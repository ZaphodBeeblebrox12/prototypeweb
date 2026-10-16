from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health_check, name="health"),
    path('', views.LandingPageView.as_view(), name='landing'),
    # path('login/', views.CustomLoginView.as_view(), name='custom_login'),
]
