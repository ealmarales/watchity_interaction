from uuid import UUID

from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import mixins, generics, viewsets, status

# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from polls import serializers
from polls_and_questions import models
from polls_and_questions.models import Choice, Poll
from users import authentication
from users.models import InteractionUser


class PollViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  # mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """ Manage Polls """

    queryset = models.Poll.objects.all()
    serializer_class = serializers.PollDetailModelSerializer
    authentication_classes = (authentication.ExternTokenAuthentication, )
    permission_classes = (IsAuthenticated,)


    def get_queryset(self):
        return super().get_queryset().filter(watchit_uuid=self.kwargs.get('watchit_uuid'))

    def retrieve(self, request, *args, **kwargs):
        """ Retrieve a poll"""
        return super().retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """ Retrieve a list of polls for one event"""
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Remove a poll """
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(request_body=serializers.PollCreateModelSerializer)
    def create(self, request, *args, **kwargs):
        """ Create a Poll """

        serializer = serializers.PollCreateModelSerializer(data=request.data)
        if serializer.is_valid():
            creator = InteractionUser.objects.get(user_id=request.user.id)
            poll = serializer.create(watchit_uuid=self.kwargs.get('watchit_uuid'),
                                         creator=creator,
                                         validated_data=request.data,
                                         )
            data = serializers.PollDetailModelSerializer(poll, context={'request': request}).data
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=serializers.PollUpdateModelSerializer)
    def update(self, request, *args, **kwargs):
        """ Update a Poll """

        poll = self.get_object()
        serializer = serializers.PollUpdateModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.update(instance=poll,
                              validated_data=request.data,
                              )
            data = serializers.PollDetailModelSerializer(poll, context={'request': request}).data
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChoiceViewSet(mixins.RetrieveModelMixin,
                      # mixins.CreateModelMixin,
                      # mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """ Manage Polls Choices """

    queryset = models.Choice.objects.all()
    serializer_class = serializers.ChoiceModelSerializer
    authentication_classes = (authentication.ExternTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return super().get_queryset().filter(poll__id=self.kwargs.get('poll_id'))


    def destroy(self, request, *args, **kwargs):
        """Remove a choice from poll  """
        return super().destroy(request, *args, **kwargs)

    # @swagger_auto_schema(request_body=serializers.QAnswerModelSerializer)
    # def create(self, request, *args, **kwargs):
    #     """ Create answer of question """
    #     serializer = serializers.QAnswerModelSerializer(data=request.data)
    #     if serializer.is_valid():
    #         creator = InteractionUser.objects.get(user_id=request.user.id)
    #         question = get_object_or_404(Question, id=self.kwargs.get('question_id'))
    #         answer = QAnswer.objects.create(question=question,
    #                                         creator=creator,
    #                                         answer=request.data.get('answer', ''),
    #                                         )
    #         data = serializers.QAnswerDetailModelSerializer(answer, context={'request': request}).data
    #         return Response(data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # @swagger_auto_schema(request_body=serializers.QAnswerModelSerializer)
    # def update(self, request, *args, **kwargs):
    #     """ Update answer of question """
    #
    #     answer = self.get_object()
    #     serializer = serializers.QAnswerModelSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.update(instance=answer,
    #                           validated_data=request.data,
    #                           )
    #         data = serializers.QAnswerDetailModelSerializer(answer, context={'request': request}).data
    #         return Response(data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # @swagger_auto_schema(request_body=None)
    # @action(detail=True, methods=['patch'])
    # def vote_unvote(self, request, *args, **kwargs):
    #     """ Vote / remove vote answer of question """
    #     answer = self.get_object()
    #     interaction_user = InteractionUser.objects.get(user_id=request.user.id)
    #     try:
    #         qavote = QAVote.objects.get(answer=answer, user=interaction_user)
    #         qavote.delete()
    #     except QAVote.DoesNotExist:
    #         QAVote.objects.create(answer=answer, user=interaction_user)
    #     data = serializers.QAnswerDetailModelSerializer(answer, context={'request': request}).data
    #     return Response(data, status=status.HTTP_200_OK)
    #
    #

