from uuid import UUID

from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import mixins, generics, viewsets, status

# Create your views here.
from rest_framework.permissions import IsAuthenticated

from polls import serializers
from polls_and_questions import models
from polls_and_questions.models import Choice, Poll
from users.authentication import ExternTokenAuthentication, ExternViewerSessionAuthentication
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
    authentication_classes = (ExternTokenAuthentication,
                              ExternViewerSessionAuthentication,
                              )

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
    authentication_classes = (ExternTokenAuthentication,
                              ExternViewerSessionAuthentication,
                              )
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return super().get_queryset().filter(poll__id=self.kwargs.get('poll_id'))


    def destroy(self, request, *args, **kwargs):
        """Remove a choice from poll  """
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(request_body=serializers.ChoiceModelSerializer)
    def create(self, request, *args, **kwargs):
        """ Create a choice of poll """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            poll = get_object_or_404(Poll, id=self.kwargs.get('poll_id'))
            choice = Choice.objects.create(poll=poll,
                                           choice=request.data.get('choice', ''),
                                           )
            data = self.serializer_class(choice).data
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=serializers.ChoiceModelSerializer)
    def update(self, request, *args, **kwargs):
        """Update a choice of poll   """
        choice = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.update(instance=choice,
                              validated_data=request.data,
                              )
            data = self.serializer_class(choice).data
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PAnswerViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  # mixins.CreateModelMixin,
                  # # mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):

    """ Manage Polls Answers """

    queryset = models.PAnswer.objects.all()
    serializer_class = serializers.PAnswerModelSerializer
    # authentication_classes = (authentication.ExternTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)


    def get_queryset(self):
        return super().get_queryset().filter(poll_id=self.kwargs.get('poll_id')).order_by('-creation_date')

    def list(self, request, *args, **kwargs):
        """ Retrieve a list of answers to poll """
        return super().list(request, *args, **kwargs)


    def retrieve(self, request, *args, **kwargs):
        """ Retrieve an answer to poll"""
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Remove an answer to poll """
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(request_body=serializers.PAnswerCreateSerializer)
    def create(self, request, *args, **kwargs):
        """ Create an answer to poll """

        serializer = serializers.PAnswerCreateSerializer(data=request.data)
        if serializer.is_valid():
            creator = InteractionUser.objects.get(user_id=request.user.id)
            poll = get_object_or_404(Poll, id=self.kwargs.get('poll_id'))
            panswer = serializer.create(poll=poll,
                                         creator=creator,
                                         validated_data=request.data,
                                         )
            data = self.serializer_class(panswer).data
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # @swagger_auto_schema(request_body=serializers.PollUpdateModelSerializer)
    # def update(self, request, *args, **kwargs):
    #     """ Update a Poll """
    #
    #     poll = self.get_object()
    #     serializer = serializers.PollUpdateModelSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.update(instance=poll,
    #                           validated_data=request.data,
    #                           )
    #         data = serializers.PollDetailModelSerializer(poll, context={'request': request}).data
    #         return Response(data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)