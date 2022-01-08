import os
import sys
import pyblish.api
import shotgun_api3
from shotgun_api3.shotgun import AuthenticationFault
from openpype.lib import OpenPypeSettingsRegistry
from openpype.api import get_project_settings, get_system_settings

if sys.version_info[0] == 2:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse


class CollectShotgridSession(pyblish.api.ContextPlugin):
    """Collect shotgrid session using user credentials"""

    order = pyblish.api.CollectorOrder
    label = "Shotgrid user session"

    def process(self, context):
        certificate_path = os.getenv("SHOTGUN_API_CACERTS")
        if not os.path.exists(certificate_path):
            certificate_path = get_shotgrid_certificate()

        if not os.path.exists(certificate_path):
            self.log.error("Could not find certificate in shotgun_api3: \
                {}".format(certificate_path))

        set_shotgrid_certificate(certificate_path)

        avalon_project = os.getenv("AVALON_PROJECT")

        shotgrid_settings = get_shotgrid_settings(avalon_project)
        shotgrid_servers_settings = get_shotgrid_servers()

        shotgrid_server = shotgrid_settings.get('shotgrid_server', "")
        shotgrid_server_setting = shotgrid_servers_settings.get(shotgrid_server, {})
        shotgrid_url = shotgrid_server_setting.get('shotgrid_url', "")
        shotgrid_script_name = shotgrid_server_setting.get('shotgrid_script_name', "")
        shotgrid_script_key = shotgrid_server_setting.get('shotgrid_script_key', "")

        login = get_login() or os.getenv("OPENPYPE_SG_USER")

        if not login:
            self.log.error("No Shotgrid login found, please login to shotgrid withing openpype Tray")

        session = shotgun_api3.Shotgun(
            base_url=shotgrid_url,
            script_name=shotgrid_script_name,
            api_key=shotgrid_script_key,
            sudo_as_login=login
        )

        try:
            session.preferences_read()
        except AuthenticationFault:
            raise ValueError("Could not connect to shotgrid {} with user {}".format(shotgrid_url, login))

        self.log.info("Logged to shotgrid {} with user {}".format(shotgrid_url, login))
        context.data['shotgridSession'] = session


def get_shotgrid_certificate():
    shotgun_api_path = os.path.dirname(shotgun_api3.__file__)
    return os.path.join(shotgun_api_path, "lib", "certifi", "cacert.pem")


def set_shotgrid_certificate(certificate):
    os.environ["SHOTGUN_API_CACERTS"] = certificate


def get_shotgrid_settings(project):
    return get_project_settings(project).get('shotgrid', {})


def get_shotgrid_servers():
    return get_system_settings().get('modules', {}).get('shotgrid', {}).get('shotgrid_settings', {})


def get_login():
    reg = OpenPypeSettingsRegistry()
    try:
        return str(reg.get_item("shotgrid_login"))
    except Exception as e:
        return None
