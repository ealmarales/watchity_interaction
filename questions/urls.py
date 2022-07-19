"""Experience URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from questions import views

router = DefaultRouter()
router.register('question', views.QuestionViewSet, basename='questions')

answer_router = DefaultRouter()
answer_router.register('answer', views.QAnswerViewSet, basename='answers')

urlpatterns = [
    path('watchit/<uuid:watchit_uuid>/', include(router.urls)),
    path('watchit/<uuid:watchit_uuid>/question/<int:question_id>/', include(answer_router.urls)),
]


