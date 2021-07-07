import shotgun_api3
from typing import AnyStr, Dict, Any
from shotgun_api3.shotgun import AuthenticationFault

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


from openpype.lib import OpenPypeSecureRegistry

_LOGIN_NAME = "login"
_PASSWORD_NAME = "password"


def get_shotgrid_hostname(shotgrid_url: AnyStr) -> AnyStr:

    if not shotgrid_url:
        raise Exception("Shotgrid url cannot be a null")

    valid_shotgrid_url = (
        f"//{shotgrid_url}" if "//" not in shotgrid_url else shotgrid_url
    )

    return urlparse(valid_shotgrid_url).hostname


def _get_shotgrid_secure_key(hostname: AnyStr, key: AnyStr) -> AnyStr:
    """Secure item key for entered hostname."""
    return f"shotgrid/{hostname}/{key}"


def get_credentials(shotgrid_url: AnyStr) -> Dict[AnyStr, Any]:
    output = {_LOGIN_NAME: None, _PASSWORD_NAME: None}
    hostname = get_shotgrid_hostname(shotgrid_url)
    if not hostname:
        return output

    username_name = _get_shotgrid_secure_key(hostname, _LOGIN_NAME)
    api_key_name = _get_shotgrid_secure_key(hostname, _PASSWORD_NAME)

    username_registry = OpenPypeSecureRegistry(username_name)
    api_key_registry = OpenPypeSecureRegistry(api_key_name)

    output[_LOGIN_NAME] = username_registry.get_item(_LOGIN_NAME, None)
    output[_PASSWORD_NAME] = api_key_registry.get_item(_PASSWORD_NAME, None)

    return output


def save_credentials(login: AnyStr, password: AnyStr, shotgrid_url: AnyStr):
    hostname = get_shotgrid_hostname(shotgrid_url)
    login_key = _get_shotgrid_secure_key(hostname, _LOGIN_NAME)
    password_key = _get_shotgrid_secure_key(hostname, _PASSWORD_NAME)

    # Clear credentials
    clear_credentials(shotgrid_url)

    login_registry = OpenPypeSecureRegistry(login_key)
    password_registry = OpenPypeSecureRegistry(password_key)

    login_registry.set_item(_LOGIN_NAME, login)
    password_registry.set_item(_PASSWORD_NAME, password)


def clear_credentials(shotgrid_url: AnyStr):
    hostname = get_shotgrid_hostname(shotgrid_url)
    login_key = _get_shotgrid_secure_key(hostname, _LOGIN_NAME)
    password_key = _get_shotgrid_secure_key(hostname, _PASSWORD_NAME)

    login_registry = OpenPypeSecureRegistry(login_key)
    password_registry = OpenPypeSecureRegistry(password_key)

    current_username = login_registry.get_item(_LOGIN_NAME, None)
    current_api_key = password_registry.get_item(_PASSWORD_NAME, None)

    if current_username is not None:
        login_registry.delete_item(_LOGIN_NAME)

    if current_api_key is not None:
        password_registry.delete_item(_PASSWORD_NAME)


def check_credentials(
    login: AnyStr, password: AnyStr, shotgrid_url: AnyStr
) -> bool:

    if not shotgrid_url or not login or not password:
        return False

    try:
        session = shotgun_api3.Shotgun(
            shotgrid_url,
            login=login,
            password=password,
        )
        session.preferences_read()
        session.close()

    except AuthenticationFault:
        return False

    return True
