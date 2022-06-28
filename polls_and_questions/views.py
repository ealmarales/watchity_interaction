from rest_framework import mixins, viewsets, status
from rest_framework.response import Response

from polls_and_questions import models
from polls_and_questions.serializers import SetupModelSerializer, SetupSerializer


class SetupViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):

    serializer_class = SetupModelSerializer

    def create(self, request, *args, **kwargs):
        serializer = SetupSerializer(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        setup = serializer.save()
        data = SetupModelSerializer(setup).data
        return Response(data, status=status.HTTP_201_CREATED)



    def get_queryset(self):
        """ Restrict list of all Setups."""
        queryset = models.Setup.objects.all()
        return queryset


