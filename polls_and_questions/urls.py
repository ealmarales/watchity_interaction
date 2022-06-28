"""Poll and Questions API URLs."""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from polls_and_questions import views

router = DefaultRouter()
router.register('config', views.SetupApiViewSet, basename='setup')

urlpatterns = [
    # path('hello', views.HelloApiView.as_view()),

    # path('config', views.SetupApiView.as_view()),

    path('', include(router.urls))

]