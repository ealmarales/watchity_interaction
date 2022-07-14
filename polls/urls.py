"""Experience URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from polls import views

router = DefaultRouter()
router.register('polls', views.PollViewSet, basename='polls')

urlpatterns = [
    path('watchit/<uuid:watchit_uuid>/', include(router.urls))
]

