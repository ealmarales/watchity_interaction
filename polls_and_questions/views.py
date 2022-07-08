from uuid import UUID

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from polls_and_questions import serializers, services
from polls_and_questions.models import EventConfig, Poll

from django.utils.translation import gettext_lazy as _


class ConfigManager(APIView):
    """ Abstract class for manage Event Configurations """

    serializer_class = None

    @staticmethod
    def _validate_watchit_uuid(watchit_uuid: UUID):
        """

        Args:
            watchit_uuid: watchit identifier.

        Raises:
            NotFound: When watchit_uuid is not found.

        Returns:

        """
        if not services.check_watchit_uuid(watchit_uuid=watchit_uuid):
            raise NotFound({'watchit_uuid': _('watchit not found')})

    @staticmethod
    def _get_event_config(watchit_uuid: UUID):
        """
        Retrieve the event config for an event.

        Args:
            watchit_uuid: watchit identifier.

        Raises:
            NotFound: When event config is not found.
        """
        try:
            return EventConfig.objects.get(watchit_uuid=watchit_uuid)
        except EventConfig.DoesNotExist:
            raise NotFound({'watchit_uuid': _('event config not found')})


class DefaultConfigPollManagerApiView(ConfigManager):
    """ Manage default polls configuration for an event.  """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_class = serializers.PollConfigModelSerializer

    def get(self, request, watchit_uuid, format=None):
        """
        Retrieve default polls configuration for an event.

        response status code:
        201 - default poll configuration is created
        204 - default poll configuration is updated
        400 - bad request
        404 - default poll not found
        """
        self._validate_watchit_uuid(watchit_uuid=watchit_uuid)
        event_config = self._get_event_config(watchit_uuid=watchit_uuid)
        if event_config.default_polls_config:
            default_poll_config = event_config.default_polls_config
            serializer = self.serializer_class(default_poll_config)
            return Response(serializer.data, status=status.HTTP_200_OK)
        raise NotFound({'watchit_uuid': _('poll config not found')})

    @swagger_auto_schema(request_body=serializers.PollConfigModelSerializer)
    def post(self, request, watchit_uuid, format=None):
        """
        Save or update default poll configuration for an event.


        If configuration event not exist is created; if default poll configuration for this event exist is updated,
        else default poll configuration for this event will be created.

        response status code:
        201 - default poll configuration is created
        204 - default poll configuration is updated
        400 - bad request


        """
        self._validate_watchit_uuid(watchit_uuid=watchit_uuid)
        serializer = self.serializer_class(data=request.data)
        response_status = None

        if serializer.is_valid():
            event, create = EventConfig.objects.get_or_create(watchit_uuid=watchit_uuid)
            default_poll_config = event.default_polls_config
            if default_poll_config:
                default_poll_config = serializer.update(instance=default_poll_config, validated_data=request.data)
                response_status = status.HTTP_200_OK
            else:
                default_poll_config = serializer.save()
                response_status = status.HTTP_201_CREATED
            event.default_polls_config = default_poll_config
            event.save()
            data = self.serializer_class(default_poll_config).data

            return Response(data=data, status=response_status)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DefaultConfigQuestionManagerApiView(ConfigManager):
    """ Manage default questions configuration for an event.  """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_class = serializers.QuestionConfigModelSerializer

    def get(self, request, watchit_uuid, format=None):
        """ Retrieve default question configuration for an event.

        response status code:
        201 - default question configuration is created
        204 - default question configuration is updated
        400 - bad request
        404 - default question not found
        """
        self._validate_watchit_uuid(watchit_uuid=watchit_uuid)
        event_config = self._get_event_config(watchit_uuid=watchit_uuid)
        if event_config.default_questions_config:
            default_question_config = event_config.default_questions_config
            serializer = self.serializer_class(default_question_config)
            return Response(serializer.data, status=status.HTTP_200_OK)
        raise NotFound({'watchit_uuid': _('question config not found')})

    @swagger_auto_schema(request_body=serializers.QuestionConfigModelSerializer)
    def post(self, request, watchit_uuid, format=None):
        """
        Save or update default question configuration for an event.


        If configuration event not exist is created; if default question configuration for this event exist is updated,
        else default question configuration for this event will be created.

        response status code:
        201 - default question configuration is created
        204 - default question configuration is updated
        400 - bad request


        """
        self._validate_watchit_uuid(watchit_uuid=watchit_uuid)
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            response_status = None

            event, create = EventConfig.objects.get_or_create(watchit_uuid=watchit_uuid)
            default_question_config = event.default_questions_config
            if default_question_config:
                default_question_config = serializer.update(instance=default_question_config,
                                                            validated_data=request.data)
                response_status = status.HTTP_200_OK
            else:
                default_question_config = serializer.save()
                response_status = status.HTTP_201_CREATED
            event.default_questions_config = default_question_config
            event.save()
            data = self.serializer_class(default_question_config).data

            return Response(data=data, status=response_status)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PollManagerApiView(ConfigManager):
    """ Manage polls
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_class = serializers.PollModelSerializer

    def get(self, request, watchit_uuid: UUID, poll_id: int, format=None):
        """
        Retrieve poll instance given a poll identifier.
        Args:
            watchit_uuid: The watchit identifier.
            poll_id: The poll identifier.
        Returns: Poll instance.
        """
        super()._validate_watchit_uuid(watchit_uuid=watchit_uuid)
        try:
            poll = Poll.objects.get(pk=poll_id)
            serializer = self.serializer_class(poll)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Poll.DoesNotExist:
            raise NotFound({'poll_id': _('poll not found')})

    # @swagger_auto_schema(request_body=serializers.PollCreateModelSerializer)
    # def post(self, request, watchit_uuid, format=None):
    #     """ Create poll in event. """
    #     super()._validate_watchit_uuid(watchit_uuid=watchit_uuid)
    #     serializer = self.serializer_class(data=request.data)
    #     if serializer.is_valid():
    #         event_config, created = EventConfig.objects.get_or_create(watchit_uuid=watchit_uuid)
    #         old_polls_config = event_config.default_polls_config
    #
    #         new_polls_config = serializer.save()
    #         event_config.default_polls_config = new_polls_config
    #         event_config.save()
    #
    #         # deleting old_polls_config
    #         if old_polls_config:
    #             old_polls_config.delete()
    #
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    #
    #
    #
    #
