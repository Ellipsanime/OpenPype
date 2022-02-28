import traceback

import requests
from typing import Dict, Any
from openpype.modules.default_modules.shotgrid.lib import (
    settings as settings_lib,
)


def _format_url(url: str) -> str:
    if not url.startswith("http://") or not url.startswith("https://"):
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


def check_batch_settings(
    url: str, script_name: str, api_key: str, project_id: int
) -> bool:
    module_url = _format_url(settings_lib.get_module_server_url())
    api_url = "/".join([module_url, "batch", "check"])
    params = {
        "shotgrid_url": url,
        "shotgrid_project_id": project_id,
        "script_name": script_name,
        "script_key": api_key,
    }

    try:
        res = requests.get(api_url, params=params)
        return {"status_code": res.status_code, "payload": res.json()}
    except requests.exceptions.RequestException:
        traceback.print_stack()


def send_batch_request(
    project: str,
    url: str,
    script_name: str,
    api_key: str,
    project_id: int,
    fields_mapping: Dict[str, Any],
    override: bool = False,
) -> int:

    module_url = _format_url(settings_lib.get_module_server_url())
    api_url = "/".join([module_url, "batch", project])
    payload = {
        "shotgrid_url": url,
        "shotgrid_project_id": project_id,
        "script_name": script_name,
        "script_key": api_key,
        "overwrite": override,
        "fields_mapping": fields_mapping,
    }

    try:
        res = requests.post(api_url, json=payload)
        return {"status_code": res.status_code, "payload": res.json()}
    except requests.exceptions.RequestException as e:
        traceback.print_stack()
