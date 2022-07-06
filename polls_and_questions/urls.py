"""Poll and Questions API URLs."""

from django.urls import path

from polls_and_questions import views

urlpatterns = [

    path('interaction/<uuid:watchit_id>/poll/configuration/', views.DefaultConfigPollManagerApiView.as_view()),
    path('watchit/<uuid:watchit_id>/qa/configuration/', views.DefaultConfigQuestionManagerApiView.as_view()),

    path('watchit/<uuid:watchit_id>/poll/configuration/<int:poll_configuration_id>/',
         views.ConfigPollManagerApiView.as_view()),
    path('watchit/<uuid:watchit_id>/qa/configuration/<int:question_configuration_id>/',
         views.ConfigQuestionManagerApiView.as_view()),





]