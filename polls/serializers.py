from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from polls_and_questions import models
from polls_and_questions.serializers import PollConfigModelSerializer
from users.models import InteractionUser
from users.serializers import InteractionUserSerializer

class PollDetailModelSerializer(serializers.ModelSerializer):

    creator = InteractionUserSerializer()
    configuration = PollConfigModelSerializer()
    answers = serializers.StringRelatedField(many=True)

    class Meta:
        model = models.Poll
        fields = ('id',
                  'creator',
                  'creation_date',
                  'question',
                  'answers',
                  'creation_date',
                  'published',
                  'streaming',
                  'configuration',
                  )
        # exclude = ('question', )

