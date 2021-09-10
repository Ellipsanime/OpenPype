from typing import Dict
from openpype_modules.shotgrid.lib import settings


def poll_server() -> int:
    return 200


def check_batch_settings(settings: Dict[str, any]) -> bool:
    return True


def send_batch_request(settings: Dict[str, any], override: bool) -> int:
    return 200
