from typing import Dict, Any
from openpype.modules.default_modules.shotgrid.lib import settings, server
from openpype.lib import create_project


class ManagerApi:

    def getProjectList(self):
        return settings.get_project_list()

    def getProjectBatchInfos(self, project):
        print("get project batch info for project ", project)
        s = settings.get_shotgrid_project_settings(project)
        auth = s.get("auth", {})
        response = {
            "url": auth.get("project_shotgrid_url", ""),
            "script_name": auth.get("project_shotgrid_script_name", ""),
            "api_key": auth.get("project_shotgrid_script_key", ""),
            "project_id": s.get("shotgrid_project_id", None),
            "fields_mapping": s.get("fields", {}),
        }
        return response

    def checkServerStatus(self):
        if server.poll_server() != 200:
            return False
        return True

    def checkProjectSettings(
        self,
        url: str,
        script_name: str,
        api_key: str,
        project_id: int,
    ):
        print("Check project ", url, script_name, api_key, project_id)
        res = server.check_batch_settings(
            url, script_name, api_key, project_id
        )
        return res

    def sendBatch(
        self,
        new_project: bool,
        project: str,
        url: str,
        script_name: str,
        api_key: str,
        project_id: int,
        fields_mapping: Dict[str, Any],
    ):
        print("Send Batch ", project, url, script_name, api_key, project_id)

        if new_project:
            print("Create project")
            create_project(project, project)

        res = server.send_batch_request(
            project, url, script_name, api_key, project_id, fields_mapping
        )
        return res
