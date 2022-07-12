from rest_framework import serializers
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
    """ Serializer for votes to """


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
