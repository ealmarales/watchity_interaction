import base64
import json
import urllib

from django.contrib.auth import get_user_model

import requests
from rest_framework import authentication
from rest_framework import exceptions

# endpoint to get the users type SYSTEM from external api
from users.models import InteractionUser

SYSTEM_USER_DATA_ENDPOINT = "https://dev-wbe.watchity.net/rest-auth/user/"
IS_EMAIL_AUTHORIZED_ENDPOINT = 'https://dev-wbe.watchity.net/v1/wbe/watchits/{watchit_uuid}/playersettings/{player_setting_uuid}/is_email_authorized/?email={email}'

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
        auth = request.META.get('HTTP_AUTHORIZATION', None)
        if not auth:
            return None
        try:
            auth_method, value = auth.split()
            if auth_method == 'Token':
                try:
                    headers = {
                        'Authorization': auth,
                        'Accept': 'application/json',
                    }
                    response = requests.get(SYSTEM_USER_DATA_ENDPOINT, headers=headers)
                    if response.status_code == 200:
                        user_data = response.json()
                        if not self.user_data_is_valid(user_data):
                            exceptions.AuthenticationFailed("Wrong response from remote server ", user_data)
                    else:
                        raise exceptions.AuthenticationFailed()
                    user, create = get_user_model().objects.get_or_create(username=user_data.get('username'))
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
            return None
        except ValueError:
            return None


class ExternViewerSessionAuthentication(authentication.BaseAuthentication):
    """"

    """

    @staticmethod
    def response_data_is_valid(json_response: dict) -> bool:
        """" Check if json_response is valid """
        expected_keys = [
            'result',
        ]
        if not type(json_response) == dict:
            return False
        for expected_key in expected_keys:
            if expected_key not in json_response.keys():
                return False
        return True

    def authenticate(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION', None)
        if not auth:
            return None
        try:
            auth_method, value = auth.split()
            if auth_method == 'ViewerSession':
                base64_bytes = value.encode('utf-8')
                view_session_bytes = base64.b64decode(base64_bytes)
                decoded = view_session_bytes.decode('utf-8')
                user_data = json.loads(decoded)

                user, create = get_user_model().objects.get_or_create(
                    username=user_data.get('form_data').get('Email'),
                    email=user_data.get('form_data').get('Email'),
                )
                InteractionUser.objects.get_or_create(
                    user=user,
                    screen_name=user_data.get('form_data').get('Name'),
                    type='PARTICIPANT',
                )
                return user, None
            return None
        except ValueError:
            return None


