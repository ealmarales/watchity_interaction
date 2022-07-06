from rest_framework import serializers
from polls_and_questions import models


class PollConfigModelSerializer(serializers.ModelSerializer):
    """Default Poll Configuration Model Serializer"""

    class Meta:
        model = models.PollConfig
        fields = '__all__'
        read_only_flields = ('id', )

class PollConfigUpdateModelSerializer(serializers.ModelSerializer):
    """Serializer for update Poll Configurations"""

    class Meta:
        model = models.PollConfig
        fields = ('privacy_mode', 'multiple_answers')

class QuestionConfigModelSerializer(serializers.ModelSerializer):
    """Default Question Configuration Model Serializer"""

    class Meta:
        model = models.QuestionConfig
        fields = '__all__'
        read_only_flields = ('id', )

class QuestionUpdateModelSerializer(serializers.ModelSerializer):
    """Question Update Model Serializer"""

    class Meta:
        model = models.QuestionConfig
        exclude = ('id', 'enabled',)

class PollModelSerializer(serializers.ModelSerializer):
    """
    Model serializer for Polls
    """
    class Meta:
        mmodel = models.Poll
        fields = '__all__'
        read_only_flields = ('id',)




