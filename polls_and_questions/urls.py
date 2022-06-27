"""Poll and Questions API URLs."""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from polls_and_questions import views

router = DefaultRouter()
router.register('setup', views.SetupViewSet, basename='setup')

urlpatterns = [
    path('', include(router.urls))
]