from uuid import UUID

from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from polls_and_questions import serializers, services
from polls_and_questions.models import EventConfig, Poll, PollConfig, Question, QuestionConfig

from django.utils.translation import gettext_lazy as _

class ConfigManager(APIView):
    """ Abstract class for manage Event Configurations """

    serializer_class = None

    def _validate_watchit_id(self, watchit_id: UUID):
        """

        Args:
            watchit_id: watchit identifier.

        Raises:
            ValidationError: When watchit_id is not found.

        Returns:

        """
        if not services.check_watchit_uuid(watchit_id=watchit_id):
            raise ValidationError({'watchit_id': _('watchit not found')})

    def _get_event_config(self, watchit_id: UUID):
        """
        Retrieve the event config for an event.

        Args:
            watchit_id: watchit identifier.

        Raises:
            ValidationError: When event config is not found.
        """
        try:
            return EventConfig.objects.get(watchit_id=watchit_id)
        except EventConfig.DoesNotExist:
            raise ValidationError({'watchit_id': _('event config not found')})


class DefaultConfigPollManagerApiView(ConfigManager):
    """ Manage default polls configuration for an event.  """


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_class = serializers.PollConfigModelSerializer

    def get(self, request, watchit_id, format=None):
        """ Retrieve default polls configuration for an event.
        """
        self._validate_watchit_id(watchit_id=watchit_id)
        event_config = self._get_event_config(watchit_id=watchit_id)
        if event_config.default_polls_config:
            default_poll_config = event_config.default_polls_config
            serializer = self.serializer_class(default_poll_config)
            return Response(serializer.data, status=status.HTTP_200_OK)
        raise ValidationError({'watchit_id': _('poll config not found')})

    @swagger_auto_schema(request_body=serializers.PollConfigModelSerializer)
    def post(self, request, watchit_id, format=None):
        """
        Save default poll configuration for an event.

        If configuration event not exist is created, if configuration event exist and have a poll configuration this is
        removed and changed for the new poll configuration.
        """
        self._validate_watchit_id(watchit_id=watchit_id)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            event_config, created = EventConfig.objects.get_or_create(watchit_id=watchit_id)
            old_polls_config = event_config.default_polls_config

            new_polls_config = serializer.save()
            event_config.default_polls_config = new_polls_config
            event_config.save()

            # deleting old_polls_config
            if old_polls_config:
                old_polls_config.delete()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, watchit_id, format=None):
        """ Enable / Disable default configuration for polls in event. """

        self._validate_watchit_id(watchit_id=watchit_id)
        event_config = self._get_event_config(watchit_id=watchit_id)
        if event_config.default_polls_config:
            default_polls_config = event_config.default_polls_config
            default_polls_config.enabled = not default_polls_config.enabled
            default_polls_config.save()

            response = {
                'enabled': default_polls_config.enabled
            }
            return Response(response, status=status.HTTP_200_OK)
        raise ValidationError({'watchit_id': _('poll config not found')})

class ConfigPollManagerApiView(ConfigManager):
    """ Manage configuration for a poll.  """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_class = serializers.PollConfigModelSerializer


    def get(self, request, watchit_id, poll_configuration_id, format=None):
        """
        Retrieve poll configuration for an event.
        Args:
            watchit_id: The watchit identifier.
            poll_configuration_id: The poll configuration identifier.
        Returns: PollConfig instance.
        """
        super()._validate_watchit_id(watchit_id=watchit_id)
        try:
            poll_config = PollConfig.objects.get(pk=poll_configuration_id)
            serializer = self.serializer_class(poll_config)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PollConfig.DoesNotExist:
            raise ValidationError({'poll_configuration_id': _('poll config not found')})





    @swagger_auto_schema(request_body=serializers.PollConfigUpdateModelSerializer)
    def put(self, request, watchit_id: UUID, poll_configuration_id: UUID, format=None):
        """
        Update poll configuration for a poll in event.

        Args:
            watchit_id (UUID): The watchit identifier.
            poll_configuration_id (UUID): The poll configuration identifier.

        Returns: PollConfig instance.

        """
        super()._validate_watchit_id(watchit_id=watchit_id)
        try:
            poll_config = PollConfig.objects.get(pk=poll_configuration_id)
            serializer = serializers.PollConfigUpdateModelSerializer(data=request.data)
            if serializer.is_valid():
                poll_config = serializer.update(poll_config, request.data)
                return Response(serializers.PollConfigModelSerializer(poll_config).data,
                                status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PollConfig.DoesNotExist:
            raise ValidationError({'poll_configuration_id': _('poll config not found')})


class DefaultConfigQuestionManagerApiView(ConfigManager):
    """ Manage default questions configuration for an event.  """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_class = serializers.QuestionConfigModelSerializer

    def get(self, request, watchit_id, format=None):
        """ Retrieve default question configuration for an event. """

        self._validate_watchit_id(watchit_id=watchit_id)
        event_config = self._get_event_config(watchit_id=watchit_id)
        if event_config.default_questions_config:
            default_question_config = event_config.default_questions_config
            serializer = self.serializer_class(default_question_config)
            return Response(serializer.data, status=status.HTTP_200_OK)
        raise ValidationError({'watchit_id': _('question config not found')})

    @swagger_auto_schema(request_body=serializers.QuestionConfigModelSerializer)
    def post(self, request, watchit_id, format=None):
        """
        Save default question configuration for an event.

        If configuration event not exist is created, if configuration event exist and have a default question
        configuration this is removed and changed for the new question configuration.
        """
        self._validate_watchit_id(watchit_id=watchit_id)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            event_config, created = EventConfig.objects.get_or_create(watchit_id=watchit_id)
            old_question_config = event_config.default_questions_config

            new_question_config = serializer.save()
            event_config.default_questions_config = new_question_config
            event_config.save()

            # deleting old_question_config
            if old_question_config:
                old_question_config.delete()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, watchit_id, format=None):
        """ Enable / Disable default configuration for questions in event. """

        self._validate_watchit_id(watchit_id=watchit_id)
        event_config = self._get_event_config(watchit_id=watchit_id)
        if event_config.default_questions_config:
            default_question_config = event_config.default_questions_config
            default_question_config.enabled = not default_question_config.enabled
            default_question_config.save()

            response = {
                'enabled': default_question_config.enabled
            }
            return Response(response, status=status.HTTP_200_OK)
        raise ValidationError({'watchit_id': _('question config not found')})

class ConfigQuestionManagerApiView(ConfigManager):
    """ Manage configuration for a Question.  """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_class = serializers.QuestionConfigModelSerializer


    def get(self, request, watchit_id, question_configuration_id, format=None):
        """
        Retrieve question configuration for an event.
        Args:
            watchit_id: The watchit identifier.
            question_configuration_id: The question configuration identifier.
        Returns: QuestionConfig instance.

        """
        super()._validate_watchit_id(watchit_id=watchit_id)
        try:
            question_config = QuestionConfig.objects.get(pk=question_configuration_id)
            serializer = self.serializer_class(question_config)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except QuestionConfig.DoesNotExist:
            raise ValidationError({'question_configuration_id': _('question config not found')})


    @swagger_auto_schema(request_body=serializers.QuestionUpdateModelSerializer)
    def put(self, request, watchit_id: UUID, question_configuration_id: UUID, format=None):
        """
        Update Question configuration for a poll in event.

        Args:
            watchit_id (UUID): The watchit identifier.
            question_configuration_id (UUID): The Question configuration identifier.

        Returns: QuestionConfig instance.

        """
        super()._validate_watchit_id(watchit_id=watchit_id)
        try:
            question_config = QuestionConfig.objects.get(pk=question_configuration_id)
            serializer = serializers.QuestionUpdateModelSerializer(data=request.data)
            if serializer.is_valid():
                question_config = serializer.update(question_config, request.data)
                return Response(serializers.QuestionConfigModelSerializer(question_config).data,
                                status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except QuestionConfig.DoesNotExist:
            raise ValidationError({'question_configuration_id': _('question config not found')})





