import os
import shotgun_api3

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


from openpype.lib import OpenPypeSecureRegistry

USERNAME_KEY = "login"
API_KEY_KEY = "password"


def get_shotgrid_hostname(shotgrid_server=None):
    if not shotgrid_server:
        shotgrid_server = os.environ.get("SHOTGRID_SERVER")

    if not shotgrid_server:
        return None

    if "//" not in shotgrid_server:
        shotgrid_server = "//" + shotgrid_server

    return urlparse(shotgrid_server).hostname


def _get_shotgrid_secure_key(hostname, key):
    """Secure item key for entered hostname."""
    return "/".join(("shotgrid", hostname, key))


def get_credentials(shotgrid_server=None):
    output = {USERNAME_KEY: None, API_KEY_KEY: None}
    hostname = get_shotgrid_hostname(shotgrid_server)
    if not hostname:
        return output

    username_name = _get_shotgrid_secure_key(hostname, USERNAME_KEY)
    api_key_name = _get_shotgrid_secure_key(hostname, API_KEY_KEY)

    username_registry = OpenPypeSecureRegistry(username_name)
    api_key_registry = OpenPypeSecureRegistry(api_key_name)

    output[USERNAME_KEY] = username_registry.get_item(USERNAME_KEY, None)
    output[API_KEY_KEY] = api_key_registry.get_item(API_KEY_KEY, None)

    return output


def save_credentials(username, api_key, shotgrid_server=None):
    hostname = get_shotgrid_hostname(shotgrid_server)
    username_name = _get_shotgrid_secure_key(hostname, USERNAME_KEY)
    api_key_name = _get_shotgrid_secure_key(hostname, API_KEY_KEY)

    # Clear credentials
    clear_credentials(shotgrid_server)

    username_registry = OpenPypeSecureRegistry(username_name)
    api_key_registry = OpenPypeSecureRegistry(api_key_name)

    username_registry.set_item(USERNAME_KEY, username)
    api_key_registry.set_item(API_KEY_KEY, api_key)


def clear_credentials(shotgrid_server=None):
    hostname = get_shotgrid_hostname(shotgrid_server)
    username_name = _get_shotgrid_secure_key(hostname, USERNAME_KEY)
    api_key_name = _get_shotgrid_secure_key(hostname, API_KEY_KEY)

    username_registry = OpenPypeSecureRegistry(username_name)
    api_key_registry = OpenPypeSecureRegistry(api_key_name)

    current_username = username_registry.get_item(USERNAME_KEY, None)
    current_api_key = api_key_registry.get_item(API_KEY_KEY, None)

    if current_username is not None:
        username_registry.delete_item(USERNAME_KEY)

    if current_api_key is not None:
        api_key_registry.delete_item(API_KEY_KEY)


def check_credentials(username, api_key, shotgrid_server=None):
    if not shotgrid_server:
        shotgrid_server = os.environ.get("SHOTGRID_SERVER")

    if not shotgrid_server or not username or not api_key:
        return False

    try:
        session = shotgun_api3.Shotgun(
            server_url=shotgrid_server, api_key=api_key, api_user=username
        )
        session.close()

    except Exception:
        return False

    return True
