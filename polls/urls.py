"""Experience URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from polls import views

router = DefaultRouter()
router.register('poll', views.PollViewSet, basename='polls')

urlpatterns = [
    path('watchit/<uuid:watchit_uuid>/', include(router.urls)),
    path('watchit/<uuid:watchit_uuid>/poll/<int:poll_id>/choice/', views.ChoiceCreatorManager.as_view()),
    path('watchit/<uuid:watchit_uuid>/poll/<int:poll_id>/choice/<int:choice_id>', views.ChoiceManagerApiView.as_view()),

]


