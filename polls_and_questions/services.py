from uuid import UUID

USER_DATA_ENDPOINT = "https://dev-wbe.watchity.net/rest-auth/user/"


def get_user_data(token: str) -> dict:
    """
    Retrieve de user data from USER_DATA_ENDPOINT

    Args:
        token: access token authentication for USER_DATA_ENDPOINT

    Returns: A dict in json format with user data.

    """

    headers = {
        'Authorization': token,
    }
    response = requests.get(USER_DATA_ENDPOINT, headers=headers)
    return response.json()


def check_watchit_uuid(watchit_uuid: UUID) -> bool:
    """
    Check if watchit_uuid is valid.

    Args:
        watchit_uuid: identifier

    Returns: True if watchit_uuid exist, False in other case.

    """
    # TODO: Implement
    return True
    # return False

import requests

def generate_request(url, params={}):
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()

def get_username(params={}):
    response = generate_request('https://randomuser.me/api', params)
    if response:
       user = response.get('results')[0]
       return user.get('name').get('first')

    return ""

if __name__ == '__main__':
    token = "Token 4407ea32f23737083ae3fffa702c18f5fd1a08ec"
    response = get_user_data(token)
    print(response.json())