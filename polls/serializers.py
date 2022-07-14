from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField, StringRelatedField

from polls_and_questions import models
from polls_and_questions.models import User, QAnswer
from polls_and_questions.serializers import UserModelSerializar, PollConfigModelSerializer


class PAnswerDetailModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PAnswer
        fields = '__all__'
        read_only_flields = ('id',)

class ChoiceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Choice
        # fields = '__all__'
        exclude = ('poll', )


class PollDetailSerializer(serializers.ModelSerializer):
    """Serializer to show polls"""
    configuration = PollConfigModelSerializer()
    creator = UserModelSerializar(read_only=True)
    answers = StringRelatedField(many=True)


    class Meta:
        model = models.Poll
        # fields = '__all__'
        fields = ('id',
                  'creator',
                  'configuration',
                  'creation_date',
                  'question',
                  'answers',
                  'published',
                  'streaming',
                  )
        read_only_flields = ('id',)

class PollCreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Poll

        class Meta:
            model = models.Question
            fields = ('question',
                      'configuration',
                      )
