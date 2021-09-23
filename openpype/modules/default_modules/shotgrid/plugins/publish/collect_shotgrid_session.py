import pyblish.api
import shotgun_api3
from openpype.modules.default_modules.shotgrid.lib import settings, credentials


class CollectShotgridSession(pyblish.api.ContextPlugin):
    """Collect shotgrid session using user credentials"""

    order = pyblish.api.CollectorOrder
    label = "Collect shotgrid user session"

    def process(self, context):
        shotgrid_url = settings.get_shotgrid_url()
        credentials_ = credentials.get_credentials(shotgrid_url)
        session = shotgun_api3.Shotgun(
            base_url=shotgrid_url,
            login=credentials_.login,
            password=credentials_.password,
        )

        context.data['shotgridSession'] = session
