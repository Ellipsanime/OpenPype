import pyblish.api
from urlparse import urlparse
import shotgun_api3
from openpype.lib import OpenPypeSecureRegistry
from openpype.api import get_system_settings


class CollectShotgridSession(pyblish.api.ContextPlugin):
    """Collect shotgrid session using user credentials"""

    order = pyblish.api.CollectorOrder
    label = "Shotgrid user session"

    def process(self, context):
        shotgrid_url = get_shotgrid_url()
        login = get_login(shotgrid_url)
        session = shotgun_api3.Shotgun(
            base_url=shotgrid_url,
            script_name="OpenPype",
            api_key="1uboigwhwbcrt@edvWrnsbmds",
            sudo_as_login=login
        )

        if not session:
            raise ValueError("Could not connect to shotgrid {} with user {}".format(shotgrid_url, login))

        self.log.info("Logged to shotgrid {} with user {}".format(shotgrid_url, login))
        context.data['shotgridSession'] = session


def get_shotgrid_settings():
    return get_system_settings().get("modules", {}).get('shotgrid', {})


def get_shotgrid_url():
    return get_shotgrid_settings().get("shotgrid_url")


def _get_shotgrid_secure_key(hostname, key):
    """Secure item key for entered hostname."""
    return "shotgrid/{}/{}".format(hostname, key)


def _get_secure_value_and_registry(
    hostname,
    name,
):
    key = _get_shotgrid_secure_key(hostname, name)
    registry = OpenPypeSecureRegistry(key)
    return registry.get_item(name, None), registry


def get_shotgrid_hostname(shotgrid_url):

    if not shotgrid_url:
        raise Exception("Shotgrid url cannot be a null")
    valid_shotgrid_url = (
        "//{}".format(shotgrid_url) if "//" not in shotgrid_url else shotgrid_url
    )
    return urlparse(valid_shotgrid_url).hostname


def get_login(shotgrid_url):
    hostname = get_shotgrid_hostname(shotgrid_url)
    if not hostname:
        return None
    login_value, _ = _get_secure_value_and_registry(
        hostname,
        "login",
    )
    return login_value
