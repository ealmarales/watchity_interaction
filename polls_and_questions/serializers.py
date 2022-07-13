from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField

from polls_and_questions import models
from polls_and_questions.models import User, QAnswer


class PollConfigModelSerializer(serializers.ModelSerializer):
    """Default Poll Configuration Model Serializer"""

    class Meta:
        model = models.PollConfig
        fields = '__all__'
        read_only_flields = ('id',)


class QuestionConfigModelSerializer(serializers.ModelSerializer):
    """Default Question Configuration Model Serializer"""

    class Meta:
        model = models.QuestionConfig
        fields = '__all__'
        read_only_flields = ('id',)


# class PollModelSerializer(serializers.ModelSerializer):
#     """
#     Model serializer for Polls
#     """
#     configuration = PollConfigModelSerializer()
#
#     class Meta:
#         model = models.Poll
#         creator = serializers.PrimaryKeyRelatedField(read_only=True)
#         fields = ('id',
#                   'creator',
#                   'watchit_uuid',
#                   'creator__id',
#                   'creator__username',
#                   'creator__scren_name',
#                   'creation_date',
#                   'published',
#                   'streaming',
#                   'configuration',
#                   )
#         read_only_fields = ('id',
#                             'watchit_uuid',
#                             'creator__id',
#                             'creator__username',
#                             'creator__scren_name',
#                             'creation_date',
#                             'published',
#                             'streaming',
#                             )

class UserModelSerializar(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = '__all__'

class QAnswerModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = QAnswer
        fields = ('answer', )




class QAnswerDetailModelSerializer(serializers.ModelSerializer):
    participant = UserModelSerializar()

    class Meta:
        model = QAnswer
        fields = ('id',
                  'participant',
                  'answer',
                  'creation_date',
                  'votes_count',
                  )
        # exclude = ('question', )




class QAVoteModelSerializer(serializers.ModelSerializer):
    """ Serializer for votes to answers to questions """
    class Meta:
        model = models.QAVote
        fields = '__all__'



class QuestionDetailModelSerializer(serializers.ModelSerializer):
    configuration = QuestionConfigModelSerializer()
    creator = UserModelSerializar(read_only=True)
    answers = QAnswerDetailModelSerializer(many=True)

    class Meta:
        model = models.Question
        # fields = '__all__'
        fields = ('id',
                  'creator',
                  'configuration',
                  'creation_date',
                  'question',
                  'answers',
                  'votes_count',
                  'published',
                  'streaming',
                  )
        # exclude = ('watchit_uuid', )


class CustomQuestionConfig(serializers.ModelSerializer):
    """
    Serializer for customize questions configurations
    """

    class Meta:
        model = models.QuestionConfig
        fields = ('allow_audience_create_questions',
                  'allow_audience_vote_questions',
                  'allow_audience_vote_answers',
                  'answers_privacy',
                  )


class QuestionModelSerializer(serializers.ModelSerializer):
    """
    Serializer for create and update questions
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
            self.fields['configuration'].update(instance=question_config, validated_data=validated_data)
        super().update(instance, validated_data)
        return instance


class QuestionCreateModelSerializer(serializers.ModelSerializer):
    """
    Serializer for questions
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
                default_event_configuration = event_config.default_questions_config
                event_config = models.EventConfig.objects.get(watchit_uuid=watchit_uuid)
                default_event_configuration = event_config.default_questions_config
                configuration = models.QuestionConfig.objects.create(
                    allow_audience_create_questions=default_event_configuration.allow_audience_create_questions,
                    allow_audience_vote_questions=default_event_configuration.allow_audience_vote_questions,
                    allow_audience_vote_answers=default_event_configuration.allow_audience_vote_answers,
                    answers_privacy=default_event_configuration.answers_privacy,
                )
            except models.EventConfig.DoesNotExist:
                raise ValidationError(
                    'define a default question configuration for this event or a custom question configuration for '
                    'this question')
            else:
                raise ValueError('define a default question configuration for this event or a custom question configuration for this question')
        question = models.Question.objects.create(
            watchit_uuid=watchit_uuid,
            creator=creator,
            question=validated_data.get('question', None),
            published=configuration.auto_publish,
            configuration=configuration
        )
        return question






