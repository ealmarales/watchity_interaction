from uuid import UUID

from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from polls_and_questions import serializers
from polls_and_questions.models import EventConfig, Poll, PollConfig, Question, QuestionConfig

from django.utils.translation import gettext_lazy as _

class SetupApiViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    serializer_class = serializers.SetupModelSerializer
    queryset = EventConfig.objects.all()

    def perform_create(self, serializer):
        """ Create a default configuration for an event """
        serializer.save()

    @action(detail=True, methods=['PATCH', ])
    def default_polls_config(self, request, pk):
        """
        Enable / Disable default configuration for polls in event.
        """
        default_polls_config = self.get_object().default_polls_config
        default_polls_config.enabled = not default_polls_config.enabled
        default_polls_config.save()

        response = {
            'enabled': default_polls_config.enabled
        }
        return Response(response)

    @action(detail=True, methods=['PATCH'])
    def default_questions_config(self, request, pk):
        """
        Enable / Disable default configuration for questions in event.
        """
        default_questions_config = self.get_object().default_questions_config
        default_questions_config.enabled = not default_questions_config.enabled
        default_questions_config.save()

        response = {
            'enabled': default_questions_config.enabled
        }
        return Response(response)




class EventConfigModelViewSet(ModelViewSet):
    """ Manage configurations for an EventConfig """

    model = EventConfig
    serializer_class = serializers.SetupModelSerializer
    queryset = EventConfig.objects.all()


class DefaultConfigPollManagerApiView(APIView):
    """ Manage default polls configuration for an event.  """

    serializer_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_class = serializers.DefaultPollConfigModelSerializer


    def get_object(self, watchit_id: UUID) -> EventConfig:
        """
        Retrieve de EventConfig instance for watchit_id.

        Args:
            watchit_id (UUID):  The watchit identifier.
        Raises:
              ValidationError: when EventConfig instance is not found.
        Returns: EventConfig instance

        """

        try:
            event_config = EventConfig.objects.get(watchit_id=watchit_id)
            return event_config
        except EventConfig.DoesNotExist:
            raise ValidationError({'watchit_id': _('Event not found')})


    def get(self, request, watchit_id, format=None):
        """ Retrieve default polls configuration for an event. """

        event_config = self.get_object(watchit_id=watchit_id)
        default_poll_config = event_config.default_polls_config
        serializer = self.serializer_class(default_poll_config)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @swagger_auto_schema(request_body=serializers.DefaultPollConfigModelSerializer)
    def post(self, request, watchit_id, format=None):
        """ Save default poll configuration for an event.
        """
        event_config = self.get_object(watchit_id=watchit_id)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            old_polls_config = event_config.default_polls_config
            new_polls_config = serializer.save()
            event_config.default_polls_config = new_polls_config
            event_config.save()

            # deleting old_polls_config
            old_polls_config.delete()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, watchit_id, format=None):
        """ Enable / Disable default configuration for polls in event. """

        setup = self.get_object(watchit_id=watchit_id)
        default_polls_config = setup.default_polls_config
        default_polls_config.enabled = not default_polls_config.enabled
        default_polls_config.save()

        response = {
            'enabled': default_polls_config.enabled
        }
        return Response(response, status=status.HTTP_200_OK)


class DefaultConfigQuestionManagerApiView(APIView):
    """ Manage default questions configuration for an event.  """

    def get_object(self, watchit_id: UUID) -> EventConfig:
        """
        Retrieve de EventConfig instance for watchit_id.

        Args:
            watchit_id (UUID):  The watchit identifier.
        Raises:
              ValidationError: when EventConfig instance is not found.
        Returns: EventConfig instance

        """

        try:
            event_config = EventConfig.objects.get(watchit_id=watchit_id)
            return event_config
        except EventConfig.DoesNotExist:
            raise ValidationError({'watchit_id': _('Event not found')})

    def get(self, request, watchit_id, format=None):
        """ Retrieve default question configuration for an event. """

        event_config = self.get_object(watchit_id=watchit_id)
        default_questions_config = event_config.default_questions_config
        serializer = serializers.DefaultQuestionConfigModelSerializer(default_questions_config)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=serializers.DefaultQuestionConfigModelSerializer)
    def post(self, request, watchit_id, format=None):
        """ Save default questions configuration for an event.
        """
        event_config = self.get_object(watchit_id=watchit_id)
        serializer = serializers.DefaultQuestionConfigModelSerializer(data=request.data)
        if serializer.is_valid():
            old_questions_config = event_config.default_questions_config
            new_questions_config = serializer.save()
            event_config.default_questions_config = new_questions_config
            event_config.save()
            # deleting old default_questions_config
            old_questions_config.delete()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, watchit_id, format=None):
        """ Enable / Disable default configuration for questions in event. """

        event_config = self.get_object(watchit_id=watchit_id)
        default_questions_config = event_config.default_questions_config
        default_questions_config.enabled = not default_questions_config.enabled
        default_questions_config.save()

        response = {
            'enabled': default_questions_config.enabled
        }
        return Response(response, status=status.HTTP_200_OK)


class ConfigPollManagerApiView(APIView):
    """ Manage configuration for a poll.  """

    def get_object(self, watchit_id: UUID, poll_configutarion_id) -> PollConfig:
        """
        Retrieve de PollConfig instance for watchit_id.

        Args:
            watchit_id (UUID):  The watchit identifier.
            poll_configutarion_id (int): Default Poll Config identifier.
        Raises:
              ValidationError: when EventConfig instance is not found.
              ValidationError: when PollConfig is not found.
        Returns: PollConfig instance

        """
        try:
            EventConfig.objects.get(watchit_id=watchit_id)
            try:
                default_poll_config = PollConfig.objects.get(pk=poll_configutarion_id)
                return default_poll_config
            except PollConfig.DoesNotExist:
                raise ValidationError({'question_configuration_id': _('Poll Configuration not found')})
        except EventConfig.DoesNotExist:
            raise ValidationError({'watchit_id': _('Event not found')})

    def get(self, request, watchit_id, poll_configuration_id, format=None):
        """
        Retrieve poll configuration for an event.
        Args:
            watchit_id: The watchit identifier.
            poll_configuration_id: The poll configuration identifier.
        Returns: PollConfig instance.

        """
        poll_config = self.get_object(watchit_id=watchit_id, poll_configutarion_id=poll_configuration_id)
        serializer = serializers.DefaultPollConfigModelSerializer(poll_config)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=serializers.PollUpdateModelSerializer)
    def put(self, request, watchit_id: UUID, poll_configuration_id: UUID, format=None):
        """
        Update poll configuration for a poll in event.

        Args:
            watchit_id (UUID): The watchit identifier.
            poll_configuration_id (UUID): The poll configuration identifier.

        Returns: PollConfig instance.

        """
        poll_config = self.get_object(watchit_id=watchit_id, poll_configutarion_id=poll_configuration_id)
        serializer = serializers.PollUpdateModelSerializer(data=request.data)
        if serializer.is_valid():
            poll_config = serializer.update(poll_config, request.data)
            return Response(serializers.DefaultPollConfigModelSerializer(poll_config).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfigQuestionManagerApiView(APIView):
    """ Manage configuration for a Question.  """

    def get_object(self, watchit_id: UUID, question_configutarion_id) -> QuestionConfig:
        """
        Retrieve de QuestionConfig instance for watchit_id.

        Args:
            watchit_id (UUID):  The watchit identifier.
            question_configutarion_id (int): Default Question Config identifier.
        Raises:
              ValidationError: when EventConfig instance is not found.
              ValidationError: when QuestionConfig is not found.
        Returns: QuestionConfig instance

        """
        try:
            event_config = EventConfig.objects.get(watchit_id=watchit_id)
            try:
                default_question_config = QuestionConfig.objects.get(pk=question_configutarion_id)
                return default_question_config
            except QuestionConfig.DoesNotExist:
                raise ValidationError({'question_configuration_id': _('Question Configuration not found')})
        except EventConfig.DoesNotExist:
            raise ValidationError({'watchit_id': _('Event not found')})

    def get(self, request, watchit_id, question_configuration_id, format=None):
        """
        Retrieve poll configuration for an event.
        Args:
            watchit_id: The watchit identifier.
            question_configuration_id: The question configuration identifier.
        Returns: QuestionConfig instance.

        """
        question_config = self.get_object(watchit_id=watchit_id, question_configutarion_id=question_configuration_id)
        serializer = serializers.DefaultQuestionConfigModelSerializer(question_config)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=serializers.DefaultQuestionConfigModelSerializer)
    def put(self, request, watchit_id: UUID, question_configuration_id: UUID, format=None):
        """
        Update Question configuration for a poll in event.

        Args:
            watchit_id (UUID): The watchit identifier.
            question_configuration_id (UUID): The Question configuration identifier.

        Returns: QuestionConfig instance.

        """
        question_config = self.get_object(watchit_id=watchit_id, question_configutarion_id=question_configuration_id)
        serializer = serializers.DefaultQuestionConfigModelSerializer(data=request.data)
        if serializer.is_valid():
            question_config = serializer.update(question_config, request.data)
            return Response(serializers.DefaultQuestionConfigModelSerializer(question_config).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



