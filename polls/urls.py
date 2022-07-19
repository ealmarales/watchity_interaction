"""Experience URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from polls import views

router = DefaultRouter()
router.register('poll', views.PollViewSet, basename='polls')

choice_router = DefaultRouter()
choice_router.register('choice', views.ChoiceViewSet, basename='choices')

urlpatterns = [
    path('watchit/<uuid:watchit_uuid>/', include(router.urls)),
    path('watchit/<uuid:watchit_uuid>/poll/<int:poll_id>/', include(choice_router.urls)),
]


