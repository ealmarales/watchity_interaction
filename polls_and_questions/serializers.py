from rest_framework import serializers
from polls_and_questions import models


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


class PollModelSerializer(serializers.ModelSerializer):
    """
    Model serializer for Polls
    """
    configuration = PollConfigModelSerializer()

    class Meta:
        model = models.Poll
        creator = serializers.PrimaryKeyRelatedField(read_only=True)
        fields = ('id',
                  'creator',
                  'watchit_uuid',
                  'creator__id',
                  'creator__username',
                  'creator__scren_name',
                  'creation_date',
                  'published',
                  'streaming',
                  'configuration',
                  )
        read_only_fields = ('id',
                            'watchit_uuid',
                            'creator__id',
                            'creator__username',
                            'creator__scren_name',
                            'creation_date',
                            'published',
                            'streaming',
                            )

# class PollCreateModelSerializer(serializers.ModelSerializer):
#     """
#     Model serializer for create polls
#     """
#     answers = serializers.StringRelatedField(many=True)
#     configuration = PollConfigModelSerializer()
#     class Meta:
#         model = models.Poll
#         fields = ('creator__username',
#                   'creator__scren_name',
#                   )
#         # read_only_fields = ('id',
#         #                     'watchit_uuid',
#         #                     'creator_id',
#         #                     'creator_username',
#         #                     'creator_scren_name',
#         #                     'creation_date',
#         #                     'published',
#         #                     'streaming',
#         #                     )
#
#     def create(self, validated_data):
#         answers_data = validated_data.pop('answers')
#         poll = models.Poll.objects.create(**validated_data)
#         for answer_data in answers_data:
#             models.Choice.objects.create(poll=poll, **answer_data)
#         return poll


