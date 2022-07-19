from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from polls_and_questions import models
from polls_and_questions.serializers import PollConfigModelSerializer
from users.models import InteractionUser
from users.serializers import InteractionUserSerializer

class PollDetailModelSerializer(serializers.ModelSerializer):

    creator = InteractionUserSerializer()
    configuration = PollConfigModelSerializer()
    choices = serializers.StringRelatedField(many=True)

    class Meta:
        model = models.Poll
        fields = ('id',
                  'creator',
                  'creation_date',
                  'question',
                  'choices',
                  'creation_date',
                  'published',
                  'streaming',
                  'configuration',
                  )
        # exclude = ('question', )


class CustomPollConfig(serializers.ModelSerializer):
    """
    Serializer for customize polls configurations
    """

    class Meta:
        model = models.PollConfig
        fields = ('answers_privacy',
                  'multiple_answers',
                  'allow_no_limited_answering',
                  'answering_time_limit',
                  )

class PollCreateModelSerializer(serializers.ModelSerializer):
    """
    Serializer for create polls
    """
    configuration = CustomPollConfig(allow_null=True)

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
                default_poll_configuration = event_config.default_polls_config
                if default_poll_configuration:
                    configuration = models.PollConfig.objects.create(
                        answers_privacy=default_poll_configuration.answers_privacy,
                        multiple_answers=default_poll_configuration.multiple_answers,
                        allow_no_limited_answering=default_poll_configuration.allow_no_limited_answering,
                        answering_time_limit=default_poll_configuration.answering_time_limit,
                    )
                else:
                    raise ValidationError(
                        'define a default poll configuration for this event or a custom poll configuration for '
                        'this poll')
            except models.EventConfig.DoesNotExist:
                raise ValidationError(
                    'define a default poll configuration for this event or a custom poll configuration for '
                    'this question')
        poll = models.Poll.objects.create(
            watchit_uuid=watchit_uuid,
            creator=creator,
            question=validated_data.get('question', ''),
            published=validated_data.get('published', False),
            configuration=configuration
        )
        return poll

class PollUpdateModelSerializer(serializers.ModelSerializer):
    """
    Serializer for update questions
    """
    configuration = CustomPollConfig(allow_null=True)

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
            poll_config = instance.configuration
            self.fields['configuration'].update(instance=poll_config, validated_data=configuration_data)
        super().update(instance, validated_data)
        return instance

class ChoiceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Choice
        fields = ('choice', )

