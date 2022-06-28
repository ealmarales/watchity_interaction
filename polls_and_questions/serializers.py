from rest_framework import serializers
from polls_and_questions import models
from polls_and_questions.models import PollConfig, QuestionConfig, Setup


class PollConfigModelSerializer(serializers.ModelSerializer):
    """Poll Configuration Model Serializer"""

    class Meta:
        model = models.PollConfig
        fields = ('present_to_audience', 'multiple_answers', 'results_privacy')


class QuestionConfigModelSerializer(serializers.ModelSerializer):
    """Question Configuration Model Serializer"""

    class Meta:
        model = models.QuestionConfig
        fields = ('enabled',
                  'allow_audience_answer',
                  'allow_audience_create_questions',
                  'auto_publish',
                  'allow_audience_vote_questions',
                  'allow_audience_vote_answers',
                  'present_to_audience',
                  'allow_audience_answer',
                  'results_privacy',
                  )


class SetupModelSerializer(serializers.ModelSerializer):
    """ Setup Model Serializer """
    default_polls_config = PollConfigModelSerializer()
    default_questions_config = QuestionConfigModelSerializer()

    class Meta:
        model = models.Setup
        fields = ('watchit_id', 'default_polls_config', 'default_questions_config', )

    def create(self, validated_data):
        polls_config_data = validated_data.pop('default_polls_config', None)
        questions_config_data = validated_data.pop('default_questions_config', None)

        polls_config = PollConfig.objects.create(**polls_config_data)
        questions_config = QuestionConfig.objects.create(**questions_config_data)

        setup = Setup.objects.create(default_polls_config=polls_config,
                                     default_questions_config=questions_config,
                                     **validated_data,
                                     )
        return setup
