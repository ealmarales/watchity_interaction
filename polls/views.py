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

class ChoiceCreatorManager(APIView):
    """
    Manage Choices for poll creation
    """
    serializer_class = serializers.ChoiceModelSerializer
    authentication_classes = (authentication.ExternTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=serializers.ChoiceModelSerializer)
    def post(self, request, watchit_uuid, poll_id, format=None):
        """
        Create a choice for poll in an event.
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            poll = get_object_or_404(Poll, id=poll_id)
            Choice.objects.create(poll=poll,
                                  choice=request.data.get('choice', ''),
                                  )
            data = serializers.PollDetailModelSerializer(poll).data
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChoiceManagerApiView(APIView):
    """
    Manage created choices for poll
    """

    serializer_class = serializers.ChoiceModelSerializer
    authentication_classes = (authentication.ExternTokenAuthentication,)
    permission_classes = (IsAuthenticated,)


    def delete(self, request, watchit_uuid: UUID, poll_id: int, choice_id: int, format=None):
        """
        Remove an choice from poll.
        """
        choice = get_object_or_404(Choice, id=choice_id)
        choice.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=serializers.ChoiceModelSerializer)
    def put(self, request, watchit_uuid: UUID, poll_id: int, choice_id: int, format=None):
        """
        Update a choice for poll in an event.
        """

        choice = get_object_or_404(Choice, id=choice_id)
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.update(instance=choice, validated_data=request.data)
            poll = choice.poll
            data = serializers.PollDetailModelSerializer(poll).data
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



