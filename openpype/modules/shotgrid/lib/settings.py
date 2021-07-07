import os
from typing import Tuple, AnyStr, Dict, Any

from openpype.api import get_system_settings
from openpype.modules.shotgrid.lib.const import MODULE_NAME


def get_shotgrid_settings() -> Dict[AnyStr, Any]:
    return get_system_settings()["modules"][MODULE_NAME]


def get_shotgrid_url_from_settings() -> AnyStr:
    return get_shotgrid_settings()["shotgrid_url"]


def get_shotgrid_event_mongo_info() -> Tuple[AnyStr, AnyStr]:
    database_name = os.environ["OPENPYPE_DATABASE_NAME"]
    collection_name = "shotgrid_events"
    return database_name, collection_name
