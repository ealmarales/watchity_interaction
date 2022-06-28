from rest_framework import serializers
from polls_and_questions import models
from polls_and_questions.models import PollConfig, QuestionConfig, Setup

class PollConfigModelSerialializer(serializers.ModelSerializer):
    """Poll Configuration Model Serializer"""

    class Meta:
        model = models.PollConfig
        fields = ('present_to_audience','multiple_answers', 'results_privacy')

class QuestionConfigModelSerialializer(serializers.ModelSerializer):
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
    """Setup Model Serializer"""
    default_polls_config = PollConfigModelSerialializer()
    default_questions_config = QuestionConfigModelSerialializer()

    class Meta:
        model = models.Setup
        fields = ('watchit_id', 'default_polls_config', 'default_questions_config', )



class SetupSerializer(serializers.Serializer):
    watchit_id = serializers.IntegerField()
    default_polls_config = PollConfigModelSerialializer()
    default_questions_config = QuestionConfigModelSerialializer()

    def validate(self, attrs):
        # TODO: Validando datos

        return attrs

    def create(self, validated_data):
        polls_config_data = validated_data.get('default_polls_config')
        questions_config_data = validated_data.get('default_questions_config')

        polls_config = models.PollConfig.objects.create(**polls_config_data)
        questions_config = models.QuestionConfig.objects.create(**questions_config_data)
        setup = models.Setup.objects.create(watchit_id=validated_data.get('watchit_id'),
                                            default_polls_config=polls_config,
                                            default_questions_config=questions_config,
                                            )
        return setup








