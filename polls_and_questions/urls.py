"""Poll and Questions API URLs."""

from django.urls import path

from polls_and_questions import views


urlpatterns = [

    path('watchit/<uuid:watchit_uuid>/poll/configuration/', views.DefaultConfigPollManagerApiView.as_view()),
    path('watchit/<uuid:watchit_uuid>/qa/configuration/', views.DefaultConfigQuestionManagerApiView.as_view()),

    path('watchit/<uuid:watchit_uuid>/question/', views.QuestionCreatorManager.as_view()),

    # path('watchit/<uuid:watchit_uuid>/poll/<int:poll_id>/', views.PollManagerApiView.as_view()),
    path('watchit/<uuid:watchit_uuid>/question/<int:question_id>/', views.QuestionManagerApiView.as_view()),

    path('watchit/<uuid:watchit_uuid>/question/<int:question_id>/answers/<int:answer_id>/', views.QAnswerManagerApiView.as_view()),

]