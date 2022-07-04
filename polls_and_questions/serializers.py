from rest_framework import serializers
from polls_and_questions import models
from polls_and_questions.models import PollConfig, QuestionConfig, EventConfig


class DefaultPollConfigModelSerializer(serializers.ModelSerializer):
    """Default Poll Configuration Model Serializer"""

    class Meta:
        model = models.PollConfig
        fields = '__all__'
        read_only_flields = ('id', )


class DefaultQuestionConfigModelSerializer(serializers.ModelSerializer):
    """Default Question Configuration Model Serializer"""

    class Meta:
        model = models.QuestionConfig
        fields = '__all__'
        read_only_flields = ('id', )





class PollUpdateModelSerializer(serializers.ModelSerializer):
    """Poll Update Model Serializer"""

    class Meta:
        model = models.Poll
        fields = ('privacy_mode', 'multiple_answers')

class QuestionUpdateModelSerializer(serializers.ModelSerializer):
    """Question Update Model Serializer"""

    class Meta:
        model = models.Question
        fields = ('answering_time_limit', 'privacy_mode', 'multiple_answers')


# ---------- Not used ****
class SetupModelSerializer(serializers.ModelSerializer):
    """ EventConfig Model Serializer """
    default_polls_config = DefaultPollConfigModelSerializer()
    default_questions_config = DefaultQuestionConfigModelSerializer()

    class Meta:
        model = models.EventConfig
        fields = ('watchit_id', 'default_polls_config', 'default_questions_config', )

    def create(self, validated_data):
        polls_config_data = validated_data.pop('default_polls_config', None)
        questions_config_data = validated_data.pop('default_questions_config', None)

        polls_config = PollConfig.objects.create(**polls_config_data)
        questions_config = QuestionConfig.objects.create(**questions_config_data)

        setup = EventConfig.objects.create(default_polls_config=polls_config,
                                           default_questions_config=questions_config,
                                           **validated_data,
                                           )
        return setup

