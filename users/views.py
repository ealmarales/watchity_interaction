from rest_framework import generics

from users import serializers
from users.models import InteractionUser


class InteractionUserList(generics.ListAPIView):
    serializer_class = serializers.InteractionUserSerializer
    queryset = InteractionUser.objects.all()

    # authentication_classes = (authentication.ExternTokenAuthentication, ) TODO: uncomment here
    # permission_classes = (IsAuthenticated,) TODO: uncomment here

