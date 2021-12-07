import os
from typing import Tuple, Dict, List, Any

from pymongo import MongoClient
from openpype.api import get_system_settings, get_project_settings
from openpype.modules.default_modules.shotgrid.lib.const import MODULE_NAME


def get_project_list() -> List[str]:
    mongo_url = os.getenv("OPENPYPE_MONGO")
    client = MongoClient(mongo_url)
    db = client['avalon']
    return db.list_collection_names()


def get_shotgrid_project_settings(project: str) -> Dict[str, Any]:
    return get_project_settings(project).get(MODULE_NAME, {})


def get_shotgrid_settings() -> Dict[str, Any]:
    return get_system_settings().get("modules", {}).get(MODULE_NAME, {})


def get_shotgrid_url() -> str:
    return get_shotgrid_settings().get("shotgrid_url")


def get_module_server_url() -> str:
    return get_shotgrid_settings().get("module_server_url")


def get_shotgrid_event_mongo_info() -> Tuple[str, str]:
    database_name = os.environ["OPENPYPE_DATABASE_NAME"]
    collection_name = "shotgrid_events"
    return database_name, collection_name
