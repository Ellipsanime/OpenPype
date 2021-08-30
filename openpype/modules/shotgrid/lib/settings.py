import os
from typing import Tuple, Dict, Any

from openpype.api import get_system_settings
from openpype_modules.shotgrid.lib.const import MODULE_NAME


def get_shotgrid_settings() -> Dict[str, Any]:
    return get_system_settings().get("modules", {}).get(MODULE_NAME, {})


def get_shotgrid_url() -> str:
    return get_shotgrid_settings().get("shotgrid_url")


def get_shotgrid_event_mongo_info() -> Tuple[str, str]:
    database_name = os.environ["OPENPYPE_DATABASE_NAME"]
    collection_name = "shotgrid_events"
    return database_name, collection_name
