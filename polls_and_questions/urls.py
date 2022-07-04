"""Poll and Questions API URLs."""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from polls_and_questions import views

router = DefaultRouter()

# router.register('watchit/', views.EventConfigModelViewSet, basename='watchit')

urlpatterns = [


    # path('', include(router.urls)),

    path('watchit/<uuid:watchit_id>/poll/configuration/', views.DefaultConfigPollManagerApiView.as_view()),
    path('watchit/<uuid:watchit_id>/qa/configuration/', views.DefaultConfigQuestionManagerApiView.as_view()),

    path('watchit/<uuid:watchit_id>/poll/configuration/<int:poll_configuration_id>/',
         views.ConfigPollManagerApiView.as_view()),
    path('watchit/<uuid:watchit_id>/qa/configuration/<int:question_configuration_id>/',
         views.ConfigQuestionManagerApiView.as_view()),

]