"""Experience URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from questions import views

router = DefaultRouter()
router.register('question', views.QuestionViewSet, basename='questions')

urlpatterns = [
    path('watchit/<uuid:watchit_uuid>/', include(router.urls)),
    path('watchit/<uuid:watchit_uuid>/question/<int:question_id>/answer/', views.QAnswerCreatorManager.as_view()),
    path('watchit/<uuid:watchit_uuid>/question/<int:question_id>/answer/<int:answer_id>', views.QAnswerManagerApiView.as_view()),

]


