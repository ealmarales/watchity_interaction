from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from polls_and_questions import models
from polls_and_questions.serializers import QuestionConfigModelSerializer
from users.models import InteractionUser
from users.serializers import InteractionUserSerializer

class QAnswerDetailModelSerializer(serializers.ModelSerializer):
    voted = serializers.SerializerMethodField()

    creator = InteractionUserSerializer()

    class Meta:
        model = models.QAnswer
        fields = ('id',
                  'creator',
                  'answer',
                  'voted',
                  'creation_date',
                  'votes_count',
                  )
        # exclude = ('question', )

    def get_voted(self, obj) -> bool:
            """"
            Check if the current user logged voted the question answer or not
            """
            request = self.context.get('request', None)
            if request.user:
                try:
                    interaction_user = InteractionUser.objects.get(user_id=request.user.id)
                    try:
                        models.QAVote.objects.get(user=interaction_user, answer=obj)
                        return True
                    except models.QAVote.DoesNotExist:
                        return False
                except InteractionUser.DoesNotExist:
                    return False
            return False

class QuestionDetailModelSerializer(serializers.ModelSerializer):
    """" Serializer for details of Questions"""
    voted = serializers.SerializerMethodField()

    configuration = QuestionConfigModelSerializer()
    creator = InteractionUserSerializer()

    def get_voted(self, obj) -> bool:
        """"
        Check if the current user logged voted the question or not
        """
        request = self.context.get('request', None)
        if request.user:
            try:
                interaction_user = InteractionUser.objects.get(user_id=request.user.id)
                try:
                    models.QVote.objects.get(user=interaction_user, question=obj)
                    return True
                except models.QVote.DoesNotExist:
                    return False
            except InteractionUser.DoesNotExist:
                return False
        return False

    class Meta:
        model = models.Question
        # fields = '__all__'
        fields = ('id',
                  'creator',
                  'configuration',
                  'creation_date',
                  'question',
                  'voted',
                  'votes_count',
                  'published',
                  'streaming',
                  )
        # exclude = ('watchit_uuid', )

class CustomQuestionConfig(serializers.ModelSerializer):
    """
    Serializer for customize question configuration
    """

    class Meta:
        model = models.QuestionConfig
        fields = ('allow_audience_create_questions',
                  'allow_audience_vote_questions',
                  'allow_audience_vote_answers',
                  'answers_privacy',
                  )

class QuestionCreateModelSerializer(serializers.ModelSerializer):
    """
    Serializer for create questions
    """
    configuration = CustomQuestionConfig(allow_null=True)

    class Meta:
        model = models.Question
        fields = ('question',
                  'configuration',
                  )

    def create(self, watchit_uuid, creator, validated_data):
        configuration_data = validated_data.pop('configuration', None)
        configuration = None
        if configuration_data:
            configuration = self.fields['configuration'].create(validated_data=configuration_data)
        else:
            try:
                event_config = models.EventConfig.objects.get(watchit_uuid=watchit_uuid)
                default_question_configuration = event_config.default_questions_config
                if default_question_configuration:
                    configuration = models.QuestionConfig.objects.create(
                        allow_audience_create_questions=default_question_configuration.allow_audience_create_questions,
                        allow_audience_vote_questions=default_question_configuration.allow_audience_vote_questions,
                        allow_audience_vote_answers=default_question_configuration.allow_audience_vote_answers,
                        answers_privacy=default_question_configuration.answers_privacy,
                    )
                else:
                    raise ValidationError(
                        'define a default question configuration for this event or a custom question configuration for '
                        'this question')
            except models.EventConfig.DoesNotExist:
                raise ValidationError(
                    'define a default question configuration for this event or a custom question configuration for '
                    'this question')
        question = models.Question.objects.create(
            watchit_uuid=watchit_uuid,
            creator=creator,
            question=validated_data.get('question', None),
            published=configuration.auto_publish,
            configuration=configuration
        )
        return question

class QuestionUpdateModelSerializer(serializers.ModelSerializer):
    """
    Serializer for update questions
    """
    configuration = CustomQuestionConfig(allow_null=True)

    class Meta:
        model = models.Question
        fields = ('question',
                  'published',
                  'streaming',
                  'configuration',
                  )

    def update(self, instance, validated_data):
        configuration_data = validated_data.pop('configuration', None)
        if configuration_data:
            question_config = instance.configuration
            self.fields['configuration'].update(instance=question_config, validated_data=configuration_data)
        super().update(instance, validated_data)
        return instance

class ResponseVoteSerializer(serializers.Serializer):
    voted = serializers.BooleanField()

class QAnswerModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QAnswer
        fields = ('answer', )
