from django.contrib.auth import get_user_model

import requests
from rest_framework import authentication
from rest_framework import exceptions

# endpoint to get the users type SYSTEM from external api
from users.models import InteractionUser

SYSTEM_USER_DATA_ENDPOINT = "https://dev-wbe.watchity.net/rest-auth/user/"


class ExternTokenAuthentication(authentication.BaseAuthentication):
    """"
    Custom Authentication method that use an url (SYSTEM_USER_DATA_ENDPOINT) to obtain users data sending a token
    provided in header of request.
    """

    @staticmethod
    def user_data_is_valid(json_response: dict) -> bool:
        """" Check if json_response is valid and contain needed data for authenticated users """
        expected_keys = [
            'username',
            'email',
            'screen_name',
        ]
        if not type(json_response) == dict:
            return False
        for expected_key in expected_keys:
            if expected_key not in json_response.keys():
                return False
        return True

    def authenticate(self, request):
        auth_token = request.META.get('HTTP_AUTHORIZATION', None)
        if not auth_token:
            return None
        try:
            headers = {
                'Authorization': auth_token,
                'Accept': 'application/json',
            }
            response = requests.get(SYSTEM_USER_DATA_ENDPOINT, headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                if not self.user_data_is_valid(user_data):
                    exceptions.AuthenticationFailed("Wrong response from remote server ", user_data)
            else:
                raise exceptions.AuthenticationFailed()
            user, create = get_user_model().objects.get_or_create(username=user_data.get('username'),
                                                                  )
            user.email = user_data.get('email')
            user.save()
            try:
                interaction_user = InteractionUser.objects.get(user=user)
                interaction_user.screen_name = user_data.get('screen_name')
                interaction_user.save()
            except InteractionUser.DoesNotExist:
                InteractionUser.objects.create(user=user,
                                               screen_name=user_data.get('screen_name'),
                                               type='SYSTEM',
                                               )
        except requests.exceptions.ConnectionError:
            raise exceptions.AuthenticationFailed('Connection error')
        return user, None
