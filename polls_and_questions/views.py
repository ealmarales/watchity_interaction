from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from polls_and_questions import serializers
from polls_and_questions.models import Setup


class SetupApiViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):

    serializer_class = serializers.SetupModelSerializer
    queryset = Setup.objects.all()

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['PATCH', ])
    def default_polls_config(self, request, pk):
        """
        Enable / Disable default configuration for polls in event.
        """
        default_polls_config = self.get_object().default_polls_config
        default_polls_config.enabled = not default_polls_config.enabled
        default_polls_config.save()

        response = {
            'enabled': default_polls_config.enabled
        }
        return Response(response)

    @action(detail=True, methods=['PATCH', ])
    def default_questions_config(self, request, pk):
        """
        Enable / Disable default configuration for questions in event.
        """
        default_questions_config = self.get_object().default_questions_config
        default_questions_config.enabled = not default_questions_config.enabled
        default_questions_config.save()

        response = {
            'enabled': default_questions_config.enabled
        }
        return Response(response)
