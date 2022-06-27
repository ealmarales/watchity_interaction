from rest_framework import mixins, viewsets

from polls_and_questions import models
from polls_and_questions.serializers import SetupModelSerializer


class SetupViewSet(viewsets.ModelViewSet):

    serializer_class = SetupModelSerializer

    def get_queryset(self):
        """ """
        queryset = models.Setup.objects.all()
        return queryset


