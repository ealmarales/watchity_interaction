from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import ValidationError

from polls_and_questions import models
from polls_and_questions.serializers import PollConfigModelSerializer

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

class ChoiceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Choice
        fields = '__all__'
        read_only_fields = ['id', 'poll']


class PollCreateModelSerializer(serializers.ModelSerializer):
    """
    Serializer for create polls
    """
    configuration = CustomPollConfig(allow_null=True)
    choices = ChoiceModelSerializer(many=True)

    class Meta:
        model = models.Poll
        fields = ('question',
                  'configuration',
                  'choices',
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
        for choice in validated_data.get('choices', None):
            models.Choice.objects.create(
                poll=poll,
                choice=choice.get('choice'),
            )
        return poll


class UpdateChoiceSerializer(serializers.Serializer):
    """Serializer for update a choice"""
    id = serializers.IntegerField()
    choice = serializers.CharField(max_length=255)
    delete = serializers.BooleanField(default=False)


class PollUpdateModelSerializer(serializers.ModelSerializer):
    """
    Serializer for update questions
    """
    configuration = CustomPollConfig(allow_null=True)
    choices = UpdateChoiceSerializer(many=True)

    class Meta:
        model = models.Question
        fields = ('question',
                  'choices',
                  'published',
                  'streaming',
                  'configuration',
                  )

    def update(self, instance, validated_data):
        #  updating choices
        choices_data = validated_data.pop('choices', None)
        self.update_edited_choices(poll=instance, choices_data=choices_data)

        # updating configuration
        configuration_data = validated_data.pop('configuration', None)
        if configuration_data:
            poll_config = instance.configuration
            self.fields['configuration'].update(instance=poll_config, validated_data=configuration_data)

        super().update(instance, validated_data)


        return instance

    def update_edited_choices(self, poll, choices_data):
        choice_id_list = []
        if poll.choices.count():
            choice_id_list = list(poll.choices.value_list('id', flat=True))
        edited_choice_id_list = [choice_data.get('id') for choice_data in choices_data]

        set = choice_id_list - edited_choice_id_list
        if not set == {}:
            raise ValidationError("{set} are not questions of this poll")








class PAnswerModelSerializer(serializers.ModelSerializer):
    selected_choice = serializers.StringRelatedField(many=True, read_only=True)
    creator = InteractionUserSerializer(read_only=True)


    class Meta:
        model = models.PAnswer
        fields = ('id',
                  'selected_choice',
                  'creator',
                  'creation_date',
                  )


class PAnswerCreateSerializer(serializers.ModelSerializer):
    """Serializer for create answers to polls"""
    class Meta:
        model = models.PAnswer
        fields = ('selected_choice',)

    def create(self, poll, creator, validated_data):
        selected_choice = []
        for choice_id in validated_data.get('selected_choice'):
            selected_choice.append(models.Choice.objects.get(id=choice_id))
        panswer = models.PAnswer.objects.create(
            poll=poll,
            creator=creator,
        )

        return panswer





