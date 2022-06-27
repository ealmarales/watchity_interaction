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
        fields = ('present_to_audience','allow_audience_answer', 'results_privacy')

class SetupModelSerializer(serializers.ModelSerializer):
    """Setup Model Serializer"""
    default_polls_config = PollConfigModelSerialializer()
    default_questions_config = QuestionConfigModelSerialializer()

    class Meta:
        model = models.Setup
        fields = ('watchit_id', 'default_polls_config', 'default_questions_config', )

    def create(self, validated_data):
        polls_config_data = validated_data.pop('default_polls_config')
        questions_config_data = validated_data.pop('default_questions_config')

        polls_config = models.PollConfig.objects.create(**polls_config_data)
        questions_config = models.QuestionConfig.objects.create(**questions_config_data)
        setup = models.Setup.objects.create(default_polls_config=polls_config,
                                            default_questions_config=questions_config,
                                            **validated_data,
                                            )
        return setup

    def update(self, instance, validated_data):
        polls_config_data = validated_data.pop('default_polls_config')
        questions_config_data = validated_data.pop('default_questions_config')

        return instance








