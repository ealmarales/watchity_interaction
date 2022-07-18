"""Experience URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from users import views


urlpatterns = [
    path('users/', views.InteractionUserList.as_view()),

]


