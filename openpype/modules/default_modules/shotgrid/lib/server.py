import requests
from typing import Dict
from openpype_modules.shotgrid.lib import settings as settings_lib


def _format_url(url: str) -> str:
    if not url.startswith('http://') or not url.startswith('https://'):
        return "http://" + url
    return url


def poll_server() -> int:
    module_url = _format_url(settings_lib.get_module_server_url())
    url = "/".join([module_url, "docs"])
    try:
        res = requests.get(url)
    except requests.exceptions.RequestException:
        return 404
    return res.status_code


def check_batch_settings(project: str, settings: Dict[str, any]) -> bool:
    module_url = _format_url(settings_lib.get_module_server_url())
    url = "/".join([module_url, "batch", project, "check"])
    params = {
        "shotgrid_url": settings.get("auth", {}).get("project_shotgrid_url"),
        "shotgrid_project_id": settings.get("shotgrid_project_id"),
        "script_name": settings.get("auth", {}).get(
            "project_shotgrid_script_name"
        ),
        "script_key": settings.get("auth", {}).get(
            "project_shotgrid_script_key"
        ),
    }

    try:
        res = requests.get(url, params=params)
    except requests.exceptions.RequestException:
        return False

    if res.status_code == 200:
        return res.json().get("status", "KO") == "OK"
    else:
        return False


def send_batch_request(
    project: str, settings: Dict[str, any], override: bool
) -> int:

    module_url = _format_url(settings_lib.get_module_server_url())
    url = "/".join([module_url, "batch", project])
    payload = {
        "shotgrid_url": settings.get("auth", {}).get("project_shotgrid_url"),
        "shotgrid_project_id": settings.get("shotgrid_project_id"),
        "script_name": settings.get("auth", {}).get(
            "project_shotgrid_script_name"
        ),
        "script_key": settings.get("auth", {}).get(
            "project_shotgrid_script_key"
        ),
        "overwrite": override,
        "fields_mapping": settings.get("fields", {}),
    }

    try:
        res = requests.post(url, json=payload)
    except requests.exceptions.RequestException:
        return 404

    return res.status_code
