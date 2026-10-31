from django.urls import path

from . import views

app_name = "prospects"

urlpatterns = [
    path("received/", views.received, name="received"),
    path("<slug:programme>/", views.enquiry, name="enquiry"),
]
