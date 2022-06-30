from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from polls_and_questions import serializers
from polls_and_questions.models import Setup, Poll, PollConfig, Question, QuestionConfig


class SetupApiViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    serializer_class = serializers.SetupModelSerializer
    queryset = Setup.objects.all()

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




class SetupModelViewSet(ModelViewSet):
    """ Manage configurations for an Event """

    model = Setup
    serializer_class = serializers.SetupModelSerializer
    queryset = Setup.objects.all()


class DefaultConfigPollManagerApiView(APIView):
    """ Manage default polls configuration for an event.  """

    serializer_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_class = serializers.PollConfigModelSerializer

    def get_object(self, pk: int) -> Setup:
        """
        Retrieve de Setup instance for pk.

        Args:
            pk:  The watchit identifier.
        Raises:
              Http404: when Setup instance is not found.
        Returns: Setup instance

        """
        setup = get_object_or_404(Setup, pk=pk)
        return setup


    def get(self, request, watchit_id, format=None):
        """ Retrieve default polls configuration for an event. """
                                                                                                           
        setup = self.get_object(pk=watchit_id)
        default_poll_config = setup.default_polls_config
        serializer = self.serializer_class(default_poll_config)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @swagger_auto_schema(request_body=serializers.PollConfigModelSerializer)
    def post(self, request, watchit_id, format=None):
        """ Save default poll configuration for an event.

        When the default configuration of the polls of an event changes, also most be change the configuration of all
        the polls of the event that have not been changed individually.

        """
        setup = self.get_object(pk=watchit_id)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            old_polls_config = setup.default_polls_config
            new_polls_config = serializer.save()
            setup.default_polls_config = new_polls_config
            setup.save()
            # updating the polls of the event that have not been changed individually
            Poll.objects.filter(poll_config=old_polls_config).update(poll_config=new_polls_config)

            old_polls_config.delete()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, watchit_id, format=None):
        """ Enable / Disable default configuration for polls in event. """

        setup = self.get_object(pk=watchit_id)
        default_polls_config = setup.default_polls_config
        default_polls_config.enabled = not default_polls_config.enabled
        default_polls_config.save()

        response = {
            'enabled': default_polls_config.enabled
        }
        return Response(response, status=status.HTTP_200_OK)


class DefaultConfigQuestionManagerApiView(APIView):
    """ Manage default questions configuration for an event.  """

    serializer_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_class = serializers.QuestionConfigModelSerializer

    def get_object(self, pk: int) -> Setup:
        """
        Retrieve de Setup instance for pk.

        Args:
            pk:  The watchit identifier.
        Raises:
              Http404: when Setup instance is not found.
        Returns: Setup instance

        """
        setup = get_object_or_404(Setup, pk=pk)
        return setup

    def get(self, request, watchit_id, format=None):
        """ Retrieve default question configuration for an event. """

        setup = self.get_object(pk=watchit_id)
        default_questions_config = setup.default_questions_config
        serializer = self.serializer_class(default_questions_config)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=serializers.QuestionConfigModelSerializer)
    def post(self, request, watchit_id, format=None):
        """ Save default questions configuration for an event.

        When the default configuration of the questions of an event changes, also most be change the configuration of all
        the questions of the event that have not been changed individually.
        """
        setup = self.get_object(pk=watchit_id)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            old_questions_config = setup.default_questions_config
            new_questions_config = serializer.save()
            setup.default_questions_config = new_questions_config
            setup.save()
            # updating the questions of the event that have not been changed individually
            Question.objects.filter(question_config=old_questions_config).update(question_config=new_questions_config)

            old_questions_config.delete()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, watchit_id, format=None):
        """ Enable / Disable default configuration for questions in event. """

        setup = self.get_object(pk=watchit_id)
        default_questions_config = setup.default_questions_config
        default_questions_config.enabled = not default_questions_config.enabled
        default_questions_config.save()

        response = {
            'enabled': default_questions_config.enabled
        }
        return Response(response, status=status.HTTP_200_OK)


class ConfigPollManagerApiView(APIView):
    """ Manage configuration for a poll.  """

    serializer_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_class = serializers.PollConfigModelSerializer

    def get_setup_object(self, pk: int) -> Setup:
        """
        Retrieve de Setup instance for pk.

        Args:
            pk:  The watchit identifier.
        Raises:
              Http404: when Setup instance is not found.
        Returns: Setup instance

        """
        setup = get_object_or_404(Setup, pk=pk)
        return setup

    def get_poll_config_object(self, pk: int) -> PollConfig:
        """
        Retrieve de PollConfig instance for pk.

        Args:
            pk:  The PollConfig identifier.
        Raises:
              Http404: when PollConfig instance is not found.
        Returns: PollConfig instance

        """
        poll_config = get_object_or_404(PollConfig, pk=pk)
        return poll_config


    def get(self, request, watchit_id, poll_configuration_id, format=None):
        """
        Retrieve poll configuration for a poll in event.
        Args:
            watchit_id: The watchit identifier.
            poll_configuration_id: The poll configuration identifier.
        Returns: PollConfig instance.

        """
        self.get_setup_object(pk=watchit_id)  # cheking event exist
        poll_config = self.get_poll_config_object(pk=poll_configuration_id)  # cheking poll_config exist

        serializer = self.serializer_class(poll_config)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=serializers.PollConfigModelSerializer)
    def put(self, request, watchit_id: int, poll_configuration_id: int, format=None):
        """
        Update poll configuration for a poll in event.

        Args:
            watchit_id (int): The watchit identifier.
            poll_configuration_id (int): The poll configuration identifier.

        Returns: PollConfig instance.

        """
        self.get_setup_object(pk=watchit_id)  # cheking event exist
        poll_config = self.get_poll_config_object(pk=poll_configuration_id)  # cheking poll_config exist
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            poll_config = serializer.update(poll_config, request.data)
            return Response(self.serializer_class(poll_config).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfigQuestionManagerApiView(APIView):
    """ Manage configuration for a question.  """

    serializer_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_class = serializers.QuestionConfigModelSerializer

    def get_setup_object(self, pk: int) -> Setup:
        """
        Retrieve de Setup instance for pk.

        Args:
            pk:  The watchit identifier.
        Raises:
              Http404: when Setup instance is not found.
        Returns: Setup instance

        """
        setup = get_object_or_404(Setup, pk=pk)
        return setup

    def get_question_config_object(self, pk: int) -> QuestionConfig:
        """
        Retrieve de QuestionConfig instance for pk.

        Args:
            pk:  The QuestionConfig identifier.
        Raises:
              Http404: when QuestionConfig instance is not found.
        Returns: QuestionConfig instance

        """
        question_config = get_object_or_404(QuestionConfig, pk=pk)
        return question_config


    def get(self, request, watchit_id, question_configuration_id, format=None):
        """
        Retrieve question configuration for a question in event.
        Args:
            watchit_id: The watchit identifier.
            question_configuration_id: The Question configuration identifier.
        Returns: QuestionConfig instance.

        """
        self.get_setup_object(pk=watchit_id)  # cheking event exist
        question_config = self.get_question_config_object(pk=question_configuration_id)  # cheking question_config exist

        serializer = self.serializer_class(question_config)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=serializers.QuestionConfigModelSerializer)
    def put(self, request, watchit_id: int, question_configuration_id: int, format=None):
        """
        Update question configuration for a question in event.

        Args:
            watchit_id (int): The watchit identifier.
            question_configuration_id (int): The question configuration identifier.

        Returns: QuestionConfig instance.

        """
        self.get_setup_object(pk=watchit_id)  # cheking event exist
        question_config = self.get_question_config_object(pk=question_configuration_id)  # cheking question_config exist
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            question_config = serializer.update(question_config, request.data)
            return Response(self.serializer_class(question_config).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


