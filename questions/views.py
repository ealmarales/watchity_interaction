from uuid import UUID

from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import mixins, generics, viewsets, status

# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from polls_and_questions import models
from polls_and_questions.models import QVote, Question, QAnswer
from questions import serializers
from users import authentication
from users.models import InteractionUser


class QuestionViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      # mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """ Manage Questions """

    queryset = models.Question.objects.all()
    serializer_class = serializers.QuestionDetailModelSerializer
    authentication_classes = (authentication.ExternTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return super().get_queryset().filter(watchit_uuid=self.kwargs.get('watchit_uuid'))

    def list(self, request, *args, **kwargs):
        """ Retrieve a list of questions"""
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Remove a question """
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(request_body=serializers.QuestionCreateModelSerializer)
    def create(self, request, *args, **kwargs):
        """ Create a Question """

        serializer = serializers.QuestionCreateModelSerializer(data=request.data)
        if serializer.is_valid():
            creator = InteractionUser.objects.get(user_id=request.user.id)
            question = serializer.create(watchit_uuid=self.kwargs.get('watchit_uuid'),
                                         creator=creator,
                                         validated_data=request.data,
                                         )
            data = serializers.QuestionDetailModelSerializer(question, context={'request': request}).data
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=serializers.QuestionUpdateModelSerializer)
    def update(self, request, *args, **kwargs):
        """ Update a Question """

        question = self.get_object()
        serializer = serializers.QuestionUpdateModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.update(instance=question,
                              validated_data=request.data,
                              )
            data = serializers.QuestionDetailModelSerializer(question, context={'request': request}).data
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=serializers.ResponseVoteSerializer)
    @action(detail=True, methods=['patch'])
    def vote_unvote(self, request, *args, **kwargs):
        """" Vote / remove vote for a question """
        question = self.get_object()
        interaction_user = InteractionUser.objects.get(user_id=request.user.id)
        try:
            qvote = QVote.objects.get(question=question, user=interaction_user)
            qvote.delete()
            data = {'voted': False}
        except QVote.DoesNotExist:
            QVote.objects.create(question=question, user=interaction_user)
            data = {'voted': True}
        return data


class QAnswerCreatorManager(APIView):
    """
    Manage Answer to Questions creation
    """
    serializer_class = serializers.QAnswerModelSerializer
    authentication_classes = (authentication.ExternTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=serializers.QAnswerModelSerializer)
    def post(self, request, watchit_uuid, question_id, format=None):
        """
        Create an answer to question in an event.
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
                question = get_object_or_404(Question, id=question_id)
                creator = InteractionUser.objects.get(user_id=request.user.id)
                answer = QAnswer.objects.create(question=question,
                                                creator=creator,
                                                answer=request.data.get('answer', ''),
                                                )
                data = serializers.QAnswerDetailModelSerializer(answer).data
                return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QAnswerManagerApiView(APIView):
    """
    Manage created answers for questions
    """

    serializer_class = serializers.QAnswerDetailModelSerializer
    authentication_classes = (authentication.ExternTokenAuthentication,)
    permission_classes = (IsAuthenticated,)


    def delete(self, request, watchit_uuid: UUID, question_id: int, answer_id: int, format=None):
        """
        Remove an answer from question.
        """
        answer = get_object_or_404(QAnswer, id=answer_id)
        answer.delete()
        return Response(status=status.HTTP_200_OK)















