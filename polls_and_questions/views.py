from uuid import UUID

import requests
from django.db import IntegrityError
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets, generics
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotFound, NotAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from polls_and_questions import serializers, services
from polls_and_questions.models import EventConfig, Poll, Question, User, QAnswer, QAVote

from django.utils.translation import gettext_lazy as _

from polls_and_questions.services import get_user_data


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

    def _get_token(self, request) -> str:
        """
        Retrieve the authentication token provided
        Returns: Token provided or None if not found.
        """
        return request.META.get('HTTP_AUTHORIZATION', None)




class DefaultConfigPollManagerApiView(ConfigManager):
    """ Manage default polls configuration for an event.  """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_class = serializers.PollConfigModelSerializer

    def get(self, request, watchit_uuid, format=None):
        """
        Retrieve default polls configuration for an event.
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
        Save default poll configuration for an event.
        """
        self._validate_watchit_uuid(watchit_uuid=watchit_uuid)
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            event, create = EventConfig.objects.get_or_create(watchit_uuid=watchit_uuid)
            default_poll_config = event.default_polls_config
            if default_poll_config:
                # if event is not created and have a default_poll_config; old default_poll_config is deleted.
                default_poll_config.delete()
            default_poll_config = serializer.save()
            event.default_polls_config = default_poll_config
            event.save()
            data = self.serializer_class(default_poll_config).data

            return Response(data=data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=serializers.PollConfigModelSerializer)
    def put(self, request, watchit_uuid, format=None):
        """ Update default poll configuration for an event. """

        self._validate_watchit_uuid(watchit_uuid=watchit_uuid)
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            event = self._get_event_config(watchit_uuid=watchit_uuid)
            default_poll_config = event.default_polls_config
            if default_poll_config:
                default_poll_config = serializer.update(instance=default_poll_config, validated_data=request.data)
                event.default_polls_config = default_poll_config
                event.save()
                data = self.serializer_class(default_poll_config).data
                return Response(data=data, status=status.HTTP_200_OK)
            raise NotFound(_('event config not found'))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DefaultConfigQuestionManagerApiView(ConfigManager):
    """ Manage default questions configuration for an event.  """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_class = serializers.QuestionConfigModelSerializer

    def get(self, request, watchit_uuid, format=None):
        """ Retrieve default question configuration for an event.
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
        Save default question configuration for an event.
        """
        self._validate_watchit_uuid(watchit_uuid=watchit_uuid)
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            event, create = EventConfig.objects.get_or_create(watchit_uuid=watchit_uuid)
            default_question_config = event.default_questions_config
            if default_question_config:
                raise ValidationError(_('this event have default question config'))
            default_question_config = serializer.save()
            event.default_questions_config = default_question_config
            event.save()
            data = self.serializer_class(default_question_config).data

            return Response(data=data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=serializers.QuestionConfigModelSerializer)
    def put(self, request, watchit_uuid, format=None):
        """ Update default question configuration for an event. """

        self._validate_watchit_uuid(watchit_uuid=watchit_uuid)
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            event = self._get_event_config(watchit_uuid=watchit_uuid)
            default_question_config = event.default_questions_config
            if default_question_config:
                default_question_config = serializer.update(instance=default_question_config, validated_data=request.data)
                event.default_questions_config = default_question_config
                event.save()
                data = self.serializer_class(default_question_config).data
                return Response(data=data, status=status.HTTP_200_OK)
            raise NotFound(_('default question configuration not found'))
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
            raise NotFound({'question_id': _('poll not found')})

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


class QuestionManagerApiView(ConfigManager):
    """
    Manage created questions
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_class = serializers.QuestionDetailModelSerializer

    def get(self, request, watchit_uuid: UUID, question_id: int, format=None):
        """
        Retrieve question instance given a watchit identifier and question identifier.
        """
        super()._validate_watchit_uuid(watchit_uuid=watchit_uuid)
        try:
            question = Question.objects.get(pk=question_id)
            serializer = self.serializer_class(question)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            raise NotFound({'question_id': _('question not found')})

    @swagger_auto_schema(request_body=serializers.QuestionModelSerializer)
    def put(self, request, watchit_uuid, question_id: int, format=None):
        """
        Update a question.
        """
        super()._validate_watchit_uuid(watchit_uuid=watchit_uuid)
        try:
            question = Question.objects.get(pk=question_id)
            serializer = serializers.QuestionModelSerializer(data=request.data)  # TODO: use self.serializerclass
            if serializer.is_valid():
                token = super()._get_token (request)
                if token:
                    try:
                        response = get_user_data(auth_token=token)
                        if response.status_code == 200:
                            user_data = response.json()
                            creator, create = User.objects.get_or_create(username=user_data.get('username'),
                                                                         screen_name=user_data.get('screen_name'),
                                                                         email=user_data.get('email'),
                                                                         type='SYSTEM',
                                                                         )
                            serializer.update(instance=question,
                                              validated_data=request.data,
                                              )
                            data = serializers.QuestionDetailModelSerializer(question).data
                            return Response(data, status=status.HTTP_200_OK)
                            # return Response(response.json(), status=status.HTTP_200_OK)
                        else:
                            return Response(status=response.status_code)
                    except requests.exceptions.ConnectionError as error:
                        return Response(error.__str__(), status=status.HTTP_404_NOT_FOUND)
                raise NotAuthenticated()
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Question.DoesNotExist:
            raise NotFound({'question_id': _('question not found')})

    def delete(self, request, watchit_uuid: UUID, question_id: int, format=None):
        """
        Remove question instance given a watchit identifier and question identifier.
        """
        super()._validate_watchit_uuid(watchit_uuid=watchit_uuid)
        try:
            question = Question.objects.get(pk=question_id)
            question.delete()
            return Response(status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            raise NotFound({'question_id': _('question not found')})
class QuestionCreatorManager(ConfigManager):
    """
    Manage Questions creation
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_class = serializers.QuestionCreateModelSerializer



    @swagger_auto_schema(request_body=serializers.QuestionCreateModelSerializer)
    def post(self, request, watchit_uuid, format=None):
        """
        Create a  question in an event.
        """
        self._validate_watchit_uuid(watchit_uuid=watchit_uuid)
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            token = super()._get_token(request)
            if token:
                try:
                    response = get_user_data(auth_token=token)
                    if response.status_code == 200:
                        user_data = response.json()
                        creator, create = User.objects.get_or_create(username=user_data.get('username'),
                                                                     screen_name=user_data.get('screen_name'),
                                                                     email=user_data.get('email'),
                                                                     type='SYSTEM',
                                                                     )
                        question = serializer.create(watchit_uuid=watchit_uuid,
                                                   creator=creator,
                                                   validated_data=request.data,
                                                   )
                        data = serializers.QuestionDetailModelSerializer(question).data
                        return Response(data, status=status.HTTP_200_OK)
                    else:
                        return Response(status=response.status_code)
                except requests.exceptions.ConnectionError as error:
                    return Response(error.__str__(), status=status.HTTP_404_NOT_FOUND)
            raise NotAuthenticated()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QAnswerManagerApiView(ConfigManager):
    """
    Manage created answers for questions
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_class = serializers.QAnswerDetailModelSerializer

    def get_object(self, watchit_uuid: UUID, question_id: int, answer_id: int):
        super()._validate_watchit_uuid(watchit_uuid=watchit_uuid)

        answers = QAnswer.objects.filter(question_id=question_id).filter(id=answer_id)
        if answers:
            return answers[0]
        else:
            raise NotFound({'answer_id': _('answer not found')})

    def get(self, request, watchit_uuid: UUID, question_id: int, answer_id: int, format=None):
        """
        Retrieve answer to question.
        """
        answer = self.get_object(watchit_uuid=watchit_uuid, question_id=question_id, answer_id=answer_id)
        data = self.serializer_class(answer).data
        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request, watchit_uuid: UUID, question_id: int, answer_id: int, format=None):
        """
        Remove an answer to question.
        """
        answer = self.get_object(watchit_uuid=watchit_uuid, question_id=question_id, answer_id=answer_id)
        data = self.serializer_class(answer).data
        answer.delete()
        return Response(data, status=status.HTTP_200_OK)


    def patch(self, request, watchit_uuid: UUID, question_id: int, answer_id: int, format=None):
        """
        Vote / Remove Vote for answer to question.
        """
        answer = self.get_object(watchit_uuid=watchit_uuid, question_id=question_id, answer_id=answer_id)

        token = super()._get_token(request)
        if token:
            try:
                response = get_user_data(auth_token=token)
                if response.status_code == 200:
                    user_data = response.json()
                    creator, create = User.objects.get_or_create(username=user_data.get('username'),
                                                                 screen_name=user_data.get('screen_name'),
                                                                 email=user_data.get('email'),
                                                                 type='SYSTEM',
                                                                 )
                    vote, created = QAVote.objects.get_or_create(answer=answer, user=creator)
                    if not created:
                        vote.delete()
                    data = {'voted': created}
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    return Response(status=response.status_code)
            except requests.exceptions.ConnectionError as error:
                return Response(error.__str__(), status=status.HTTP_404_NOT_FOUND)
        raise NotAuthenticated()

    # @swagger_auto_schema(request_body=serializers.QAnswerModelSerializer)
    # def put(self, request, watchit_uuid: UUID, question_id: int, answer_id: int, format=None):
    #     """
    #     Update an answer to question.
    #     """
    #     answer = self.get_object(watchit_uuid=watchit_uuid, question_id=question_id, answer_id=answer_id)
    #     serializer = serializers.QAnswerModelSerializer(request.data)
    #     if serializer.is_valid():
    #         serializer.update(instance=answer, validated_data=request.data)
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QAnswerCreatorManager(ConfigManager):
    """
    Manage Answer to Questions creation
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_class = serializers.QAnswerModelSerializer



    @swagger_auto_schema(request_body=serializers.QAnswerModelSerializer)
    def post(self, request, watchit_uuid, question_id, format=None):
        """
        Create an answer to question in an event.
        """
        self._validate_watchit_uuid(watchit_uuid=watchit_uuid)
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            token = super()._get_token(request)
            if token:
                try:
                    response = get_user_data(auth_token=token)
                    if response.status_code == 200:
                        user_data = response.json()
                        creator, create = User.objects.get_or_create(username=user_data.get('username'),
                                                                     screen_name=user_data.get('screen_name'),
                                                                     email=user_data.get('email'),
                                                                     type='SYSTEM',
                                                                     )
                        try:
                            question = Question.objects.get(id=question_id)
                            # TODO: Verificar si se permite multiples respuestas y si delegar responsabilidad de guardar al serializer
                            answer = QAnswer.objects.create(question=question,
                                                            participant=creator,
                                                            answer=request.data.get('answer', ''),
                                                            )
                            data = serializers.QAnswerDetailModelSerializer(answer).data
                            return Response(data, status=status.HTTP_200_OK)
                        except Question.DoesNotExist:
                            raise NotFound({'question_id': _('question not found')})
                    else:
                        return Response(status=response.status_code)
                except requests.exceptions.ConnectionError as error:
                    return Response(error.__str__(), status=status.HTTP_404_NOT_FOUND)
            raise NotAuthenticated()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionList(generics.ListAPIView):
    serializer_class = serializers.QuestionDetailModelSerializer
    queryset = Question.objects.all()



    def get_queryset(self):
        return super().get_queryset().filter(watchit_uuid=self.kwargs.get('watchit_uuid'))














