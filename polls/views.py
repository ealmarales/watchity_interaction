from rest_framework import mixins, generics, viewsets

from polls import serializers
from polls_and_questions import models

class PollViewSet(mixins.ListModelMixin,
                  # mixins.CreateModelMixin,
                  # mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):

    queryset = models.Poll.objects.all()
    serializer_class = serializers.PollDetailSerializer

    def get_queryset(self):
        return super().get_queryset().filter(watchit_uuid=self.kwargs.get('watchit_uuid'))

    # def get_serializer_class(self):
    #     self.request.m
    #     return super().get_serializer_class()














