
import requests

from uuid import UUID

# endpoint to get the users type SYSTEM from extern api
SYSTEM_USER_DATA_ENDPOINT = "https://dev-wbe.watchity.net/rest-auth/user/"


def get_user_data(auth_token: str) -> dict:
    """
    Retrieve de user data from USER_DATA_ENDPOINT

    Args:
        auth_token: authentication token for SYSTEM_USER_DATA_ENDPOINT

    Raises:
        ConnectionError: when is not possible connect with DATA_ENDPOINTS

    Returns: A dict in json format with user data.

    """
    headers = {
        'Authorization': auth_token,
        'Accept': 'application/json',
    }
    try:
        response = requests.get(SYSTEM_USER_DATA_ENDPOINT, headers=headers)
        return response
    except ConnectionError:
        raise

def check_watchit_uuid(watchit_uuid: UUID, auth_token: str = "Token 4407ea32f23737083ae3fffa702c18f5fd1a08ec",) -> bool:
    """
    Check if watchit_uuid is valid.

    A watchit is valid when exist in external API.

    Args:
        watchit_uuid: identifier

    Returns: True if watchit_uuid is valid, False in other case.

    """
    # TODO: Implement
    return True


# def generate_request(url, params={}):
#     response = requests.get(url, params=params)
#
#     if response.status_code == 200:
#         return response.json()
#
# def get_username(params={}):
#     response = generate_request('https://randomuser.me/api', params)
#     if response:
#        user = response.get('results')[0]
#        return user.get('name').get('first')
#
#     return ""

if __name__ == '__main__':
    token = "Token 4407ea32f23737083ae3fffa702c18f5fd1a08ec"
    response = get_user_data(token)
    print(response.get('username', None))

    wrong_token = "Token 4407ea32f23737083ae3fffa702c18f5fd1a08e7"
    response = get_user_data(wrong_token)
    print(response.get('username', None))
